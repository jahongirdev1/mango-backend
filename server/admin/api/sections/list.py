from core.db import db
from core.handlers import BaseAPIView
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class SectionsView(BaseAPIView):
    template_name = 'admin/sections.html'

    async def get(self, request, user):
        branch_id = user['branch_id']

        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        cond, cond_vars = ['is_active'], []
        if branch_id:
            cond.append('branch_id = {}')
            cond_vars.append(branch_id)

        query = StrUtils.to_str(request.args.get('query'))
        if query:
            cond.append('title ILIKE {}')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title, photo, position, branch_id, parent_id
            FROM control.sections
            WHERE %s
            ORDER BY position
            ''' % cond,
            *cond_vars
        ))

        return self.success(request=request, user=user, data={
            'sections': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        position = IntUtils.to_int(request.json.get('position'))
        parent_id = IntUtils.to_int(request.json.get('parent_id'))

        if user['branch_id']:
            branch_id = user['branch_id']
        else:
            branch_id = IntUtils.to_int(request.json.get('branch_id'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.sections (title, photo, position, branch_id, parent_id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            ''',
            title,
            photo,
            position,
            branch_id,
            parent_id
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
