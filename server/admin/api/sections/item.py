from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class SectionView(BaseAPIView):

    async def get(self, request, user, section_id):
        section_id = IntUtils.to_int(section_id)
        if not section_id:
            return self.error(message='Отсуствует обязательный параметр "section_id"')

        section = await db.fetchrow(
            '''
            SELECT *
            FROM control.sections
            WHERE id = $1
            ''',
            section_id
        ) or {}

        return self.success(request=request, user=user, data={'section': dict(section)})

    async def put(self, request, user, section_id):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        position = IntUtils.to_int(request.json.get('position'))
        parent_id = IntUtils.to_int(request.json.get('parent_id'))

        section_id = IntUtils.to_int(section_id)
        if not section_id:
            return self.error(message='Отсуствует обязательный параметр "section_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.sections
            SET title = $2, photo = $3, position = $4, parent_id = $5
            WHERE id = $1
            RETURNING *
            ''',
            section_id,
            title,
            photo,
            position,
            parent_id
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, section_id):
        section_id = IntUtils.to_int(section_id)
        if not section_id:
            return self.error(message='Отсуствует обязательный параметр "section_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.sections
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            section_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
