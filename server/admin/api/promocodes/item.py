from core.db import db
from core.handlers import BaseAPIView
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.strs import StrUtils


class PromocodeView(BaseAPIView):

    async def get(self, request, user, promocode_id):
        promocode_id = IntUtils.to_int(promocode_id)
        if not promocode_id:
            return self.error(message='Отсуствует обязательный параметр "promocode_id"')

        promocode = await db.fetchrow(
            '''
            SELECT *
            FROM control.promocodes
            WHERE id = $1
            ''',
            promocode_id
        ) or {}

        return self.success(request=request, user=user, data={'promocode': dict(promocode)})

    async def put(self, request, user, promocode_id):
        title = StrUtils.to_str(request.json.get('title'))
        code = StrUtils.to_str(request.json.get('code'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        percent = IntUtils.to_int(request.json.get('percent'))
        min_sum = FloatUtils.to_float(request.json.get('min_sum'))
        max_sum = FloatUtils.to_float(request.json.get('max_sum'))
        discount_summ = FloatUtils.to_float(request.json.get('summ'))
        limit = IntUtils.to_int(request.json.get('limit'))
        branch_id = IntUtils.to_int(request.json.get('branch_id'))
        description = StrUtils.to_str(request.json.get('description'))
        is_disposable = BoolUtils.to_bool(request.json.get('is_disposable'))
        is_free_delivery = BoolUtils.to_bool(request.json.get('is_free_delivery'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        if not code:
            return self.error(message='Отсуствует обязательный параметры "Код"')

        promocode_id = IntUtils.to_int(promocode_id)
        if not promocode_id:
            return self.error(message='Отсуствует обязательный параметр "promocode_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.promocodes
            SET 
                title = $2, 
                code = $3, 
                in_use = $4, 
                percent = $5,
                min_sum = $6,
                max_sum = $7,
                discount_summ = $8,
                limit = $9,
                branch_id = $10,
                description = $11,
                is_disposable = $12,
                is_free_delivery = $13
            WHERE id = $1
            RETURNING *
            ''',
            promocode_id,
            title,
            code,
            in_use,
            percent,
            min_sum,
            max_sum,
            discount_summ,
            limit,
            branch_id,
            description,
            is_disposable,
            is_free_delivery
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, promocode_id):
        promocode_id = IntUtils.to_int(promocode_id)
        if not promocode_id:
            return self.error(message='Отсуствует обязательный параметр "promocode_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.promocodes
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            promocode_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
