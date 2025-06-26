from core.db import db
from core.handlers import BaseAPIView
from core.tools import set_counters
from utils.lists import ListUtils
from utils.strs import StrUtils


class WordsView(BaseAPIView):
    template_name = 'admin/words.html'

    async def get(self, request, user):
        cond, cond_vars = ['is_active'], []

        query = StrUtils.to_str(request.args.get('query'))
        if query:
            cond.append('title ILIKE {}')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title
            FROM control.words
            WHERE %s
            ORDER BY id DESC
            ''' % cond,
            *cond_vars
        ))

        return self.success(request=request, user=user, data={
            'items': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.words (title)
            VALUES ($1)
            RETURNING id
            ''',
            title,
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
