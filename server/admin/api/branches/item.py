from core.db import db
from core.handlers import BaseAPIView
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
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
        rating = FloatUtils.to_float(request.json.get('rating'))
        order_time = IntUtils.to_int(request.json.get('order_time'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))

        branch_id = IntUtils.to_int(branch_id)
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметр "branch_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.branches
            SET title = $2, photo = $3, latitude = $4, longitude = $5, order_time = $6, rating = $7, promotion_text = $8, phone = $9, in_use = $10
            WHERE id = $1
            RETURNING *
            ''',
            branch_id,
            title,
            photo,
            latitude,
            longitude,
            order_time,
            rating,
            promotion_text,
            phone,
            in_use
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
