from core.db import db
from core.handlers import BaseAPIView
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class BranchView(BaseAPIView):

    async def get(self, request, user, branch_id):
        branch_id = IntUtils.to_int(branch_id)
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметр "branch_id"')

        branch = await db.fetchrow(
            '''
            SELECT *
            FROM control.branches
            WHERE id = $1
            ''',
            branch_id
        ) or {}

        return self.success(request=request, user=user, data={'branch': dict(branch)})

    async def put(self, request, user, branch_id):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        phone = StrUtils.to_str(request.json.get('phone'))
        promotion_text = StrUtils.to_str(request.json.get('promotion_text'))
        latitude = FloatUtils.to_float(request.json.get('latitude'))
        longitude = FloatUtils.to_float(request.json.get('longitude'))
        min_order_time = IntUtils.to_int(request.json.get('min_order_time'))
        max_order_time = IntUtils.to_int(request.json.get('max_order_time'))
        min_order_sum = IntUtils.to_int(request.json.get('min_order_sum'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        is_store = BoolUtils.to_bool(request.json.get('is_store'))
        category_ids = ListUtils.to_list_of_ints(request.json.get('category_ids'))
        min_delivery_sum = FloatUtils.to_float(request.json.get('min_delivery_sum'))

        branch_id = IntUtils.to_int(branch_id)
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметр "branch_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.branches
            SET 
                title = $2,
                photo = $3,
                latitude = $4,
                longitude = $5,
                min_order_time = $6,
                promotion_text = $7,
                phone = $8,
                in_use = $9,
                max_order_time = $10,
                min_order_sum = $11,
                is_store = $12,
                category_ids = $13,
                min_delivery_sum = $14
            WHERE id = $1
            RETURNING *
            ''',
            branch_id,
            title,
            photo,
            latitude,
            longitude,
            min_order_time,
            promotion_text,
            phone,
            in_use,
            max_order_time,
            min_order_sum,
            is_store,
            category_ids,
            min_delivery_sum
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, branch_id):
        branch_id = IntUtils.to_int(branch_id)
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметр "branch_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.branches
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            branch_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
