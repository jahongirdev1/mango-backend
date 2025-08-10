from bson import ObjectId
from pymongo import ReturnDocument

from core.db import mongo, db
from core.firebase import Firebase
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class OrderView(BaseAPIView):

    async def get(self, request, user, order_id):
        order_id = StrUtils.to_str(order_id)
        if not order_id or not ObjectId.is_valid(order_id):
            return self.error(message='Отсуствует обязательный параметры "Номер заказа"')

        item = await mongo.orders.find_one({
            '_id': ObjectId(order_id)
        })

        return self.success(request=request, user=user, data={
            'order': item
        })

    async def post(self, request, user, order_id):
        order_id = StrUtils.to_str(order_id)
        if not order_id or not ObjectId.is_valid(order_id):
            return self.error(message='Отсуствует обязательный параметры "Номер заказа"')

        status = StrUtils.to_str(request.json.get('status'))
        if not status:
            return self.error(message='Отсуствует обязательный параметры "Статус"')

        action = StrUtils.to_str(request.json.get('action'))
        if action == 'change_status':
            order = await mongo.orders.find_one_and_update({'_id': ObjectId(order_id)}, {'$set': {
                'status': status
            }}, return_document=ReturnDocument.AFTER)

            if not order:
                return self.error(message='Операция не выполнена')

            token = await db.fetchval(
                '''
                SELECT *
                FROM control.clients
                WHERE id = $1
                ''',
                order['client_id']
            )

            if token:
                print('->>>>')
                Firebase.send_message(token, {
                    'action': 'change_status'
                })

            return self.success()

        if action == 'order_time':
            max_order_time = IntUtils.to_int(request.json.get('max_order_time'))
            if not max_order_time:
                return self.error(message='Отсуствует обязательный параметры "max_order_time"')

            min_order_sum = IntUtils.to_int(request.json.get('min_order_sum'))
            if not min_order_sum:
                return self.error(message='Отсуствует обязательный параметры "min_order_sum"')

            await mongo.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {
                'max_order_time': max_order_time,
                'min_order_sum': min_order_sum
            }})
            return self.success()

        return self.error(message='Операция не выполнена')
