from core.db import db
from core.handlers import BaseAPIView
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.strs import StrUtils


class GoodView(BaseAPIView):

    async def get(self, request, user, good_id):
        good_id = IntUtils.to_int(good_id)
        if not good_id:
            return self.error(message='Отсуствует обязательный параметр "good_id"')

        good = await db.fetchrow(
            '''
            SELECT *
            FROM control.goods
            WHERE id = $1
            ''',
            good_id
        ) or {}

        return self.success(request=request, user=user, data={'good': dict(good)})

    async def put(self, request, user, good_id):
        good_id = IntUtils.to_int(good_id)
        if not good_id:
            return self.error(message='Отсуствует обязательный параметр "good_id"')

        title = StrUtils.to_str(request.json.get('title'))
        price = FloatUtils.to_float(request.json.get('price'))
        description = StrUtils.to_str(request.json.get('description'))
        photo = StrUtils.to_str(request.json.get('photo'))
        whole = FloatUtils.to_float(request.json.get('whole'))
        is_new = BoolUtils.to_bool(request.json.get('is_new'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        balance = FloatUtils.to_float(request.json.get('balance'))
        section_id = IntUtils.to_int(request.json.get('section_id'))

        data = await db.fetchrow(
            '''
            UPDATE control.goods
            SET title = $2, price = $3, description = $4, photo = $5, whole = $6, is_new = $7, in_use = $8, balance = $9, section_id = $10
            WHERE id = $1
            RETURNING *
            ''',
            good_id,
            title,
            price,
            description,
            photo,
            whole,
            is_new,
            in_use,
            balance,
            section_id
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, good_id):
        good_id = IntUtils.to_int(good_id)
        if not good_id:
            return self.error(message='Отсуствует обязательный параметр "good_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.goods
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            good_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
