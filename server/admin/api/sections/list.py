from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class SectionsView(BaseAPIView):
    template_name = 'admin/sections.html'

    async def get(self, request, user):
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title, photo, position
            FROM control.sections
            WHERE is_active
            ORDER BY id DESC
            '''
        ))

        return self.success(request=request, user=user, data={
            'sections': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        position = IntUtils.to_int(request.json.get('position'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.sections (title, photo, position)
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
