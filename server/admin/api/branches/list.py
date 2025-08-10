from datetime import datetime

from core.db import db
from core.handlers import BaseAPIView
from core.tools import set_counters
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class BranchesView(BaseAPIView):
    template_name = 'admin/branches.html'

    async def get(self, request, user):
        query = StrUtils.to_str(request.args.get('query'))

        cond, cond_vars = ['is_active'], []
        if query:
            cond.append('title ILIKE {}')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT 
                id, 
                title, 
                photo, 
                latitude, 
                longitude, 
                min_order_time, 
                rating, 
                promotion_text, 
                phone, 
                in_use, 
                is_active, 
                updated_at, 
                created_at, 
                category_ids, 
                icon, 
                max_order_time, 
                min_order_sum, 
                is_store, 
                min_delivery_sum, 
                distance_cost,
                location_name
            FROM control.branches
            WHERE %s
            ORDER BY id DESC
            ''' % cond,
            *cond_vars
        ))

        return self.success(request=request, user=user, data={
            'branches': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        phone = StrUtils.to_str(request.json.get('phone'))
        promotion_text = StrUtils.to_str(request.json.get('promotion_text'))
        location_name = StrUtils.to_str(request.json.get('location_name'))
        latitude = FloatUtils.to_float(request.json.get('latitude'))
        longitude = FloatUtils.to_float(request.json.get('longitude'))
        min_order_time = IntUtils.to_int(request.json.get('min_order_time'))
        max_order_time = IntUtils.to_int(request.json.get('max_order_time'))
        min_order_sum = IntUtils.to_int(request.json.get('min_order_sum'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        is_store = BoolUtils.to_bool(request.json.get('is_store'))
        category_ids = ListUtils.to_list_of_ints(request.json.get('category_ids'))
        min_delivery_sum = FloatUtils.to_float(request.json.get('min_delivery_sum'))
        distance_cost = FloatUtils.to_float(request.json.get('distance_cost'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.branches 
            (title, photo, latitude, longitude, min_order_time, promotion_text, phone, in_use, category_ids, 
            max_order_time, min_order_sum, is_store, min_delivery_sum, distance_cost, location_name)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id
            ''',
            title,
            photo,
            latitude,
            longitude,
            min_order_time,
            promotion_text,
            phone,
            in_use,
            category_ids,
            max_order_time,
            min_order_sum,
            is_store,
            min_delivery_sum,
            distance_cost,
            location_name
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        await db.executemany(
            '''
            INSERT INTO control.work_schedule (branch_id, day, started_at, stopped_at)
            VALUES ($1, $2, $3, $4)
            ''',
            [
                (
                    inserted_id,
                    index,
                    datetime.strptime('00:00', '%H:%M').time(),
                    datetime.strptime('23:59:59', '%H:%M:%S').time()
                )
                for index in range(1, 8)
            ]
        )

        return self.success(data={})
