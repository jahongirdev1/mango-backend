from core.db import db
from core.handlers import BaseAPIView
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class BranchesView(BaseAPIView):
    template_name = 'admin/branches.html'

    async def get(self, request, user):
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title, photo, latitude, longitude, order_time, rating, promotion_text, phone, in_use, updated_at, created_at
            FROM control.branches
            WHERE is_active
            ORDER BY id DESC
            '''
        ))

        return self.success(request=request, user=user, data={
            'branches': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        phone = StrUtils.to_str(request.json.get('phone'))
        promotion_text = StrUtils.to_str(request.json.get('promotion_text'))
        latitude = FloatUtils.to_float(request.json.get('latitude'))
        longitude = FloatUtils.to_float(request.json.get('longitude'))
        rating = FloatUtils.to_float(request.json.get('rating'))
        order_time = IntUtils.to_int(request.json.get('order_time'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        section_id = IntUtils.to_int(request.json.get('section_id'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.branches (title, photo, latitude, longitude, order_time, rating, promotion_text, phone, in_use, section_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
            ''',
            title,
            photo,
            latitude,
            longitude,
            order_time,
            rating,
            promotion_text,
            phone,
            in_use,
            section_id
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
