from core.db import db
from core.handlers import BaseAPIView
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class CategoriesView(BaseAPIView):
    template_name = 'admin/categories.html'

    async def get(self, request, user):
        cond, cond_vars = ['is_active'], []
        query = StrUtils.to_str(request.args.get('query'))
        ids = StrUtils.to_str(request.args.get('ids'))
        ids = ids and ListUtils.to_list_of_ints(ids.split(','))

        if query:
            cond.append('title ILIKE {}')
            cond_vars.append(f'%{query}%')

        if ids:
            cond.append('id = ANY ($1)')
            cond_vars.append(ids)

        cond, _ = set_counters(' AND '.join(cond))

        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title, photo, position
            FROM control.categories
            WHERE %s
            ORDER BY position
            ''' % cond,
            *cond_vars
        ))

        return self.success(request=request, user=user, data={
            'categories': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        position = IntUtils.to_int(request.json.get('position'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Название"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.categories (title, photo, position)
            VALUES ($1, $2, $3)
            RETURNING id
            ''',
            title,
            photo,
            position
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
