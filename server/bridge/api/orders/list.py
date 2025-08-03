from datetime import datetime

import ujson

from core.cache import cache
from core.db import db, mongo
from core.handlers import TemplateHTTPView
from core.pager import Pager
from utils.ints import IntUtils
from utils.strs import StrUtils

__all__ = [
    'OrdersBridgeView'
]


class OrdersBridgeView(TemplateHTTPView):

    async def get(self, request, client_id):
        client_id = IntUtils.to_int(client_id)
        if not client_id:
            return self.error(message='Отсуствует обязательный параметр "client_id"')

        pager = Pager()
        pager.set_page(request.args.get('page', 1))
        pager.set_limit(request.args.get('limit', 100))
        offset = IntUtils.to_int(request.args.get('offset')) or pager.offset

        filters = {
            'is_active': True,
            'client_id': client_id,
        }

        items = await mongo.orders.find(filters).skip(offset) \
            .limit(pager.limit) \
            .sort('_id', -1) \
            .to_list(length=None)

        return self.success(
            data={
                'items': items
            }
        )

    async def post(self, request, client_id):
        client_id = IntUtils.to_int(client_id)
        if not client_id:
            return self.error(message='Отсуствует обязательный параметр "client_id"')

        uid = StrUtils.to_str(request.json.get('uid'))
        if not uid:
            return self.error(message='Отсуствует обязательный параметр "uid"')

        data = await cache.get(f'order:calc:{uid}')
        if not data:
            return self.error(message='Операция не выполнена')

        data = ujson.loads(data)
        type_pay = StrUtils.to_str(request.json.get('type_pay'), default='CACHE')

        data['type_pay'] = type_pay
        data['client_id'] = client_id
        data['uid'] = uid
        data['created_at'] = datetime.now()
        data['status'] = 'CREATED'
        data['is_active'] = True

        order = await mongo.orders.insert_one(data)

        if not order.inserted_id:
            return self.error(message='Операция не выполнена')

        await db.execute(
            '''
            DELETE FROM control.items
            WHERE uid = $1
            RETURNING id
            ''',
            uid
        )
        await cache.delete(f'order:calc:{uid}')

        return self.success()

    async def delete(self, request, client_id):
        client_id = IntUtils.to_int(client_id)
        if not client_id:
            return self.error(message='Отсуствует обязательный параметр "client_id"')

        await mongo.orders.update_many({'client_id': client_id}, {'$set': {
            'is_active': False,
            'updated_at': datetime.now()
        }})

        return self.success()
