from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class CategoryView(BaseAPIView):

    async def get(self, request, user, category_id):
        category_id = IntUtils.to_int(category_id)
        if not category_id:
            return self.error(message='Отсуствует обязательный параметр "category_id"')

        section = await db.fetchrow(
            '''
            SELECT *
            FROM control.categories
            WHERE id = $1
            ''',
            category_id
        ) or {}

        return self.success(request=request, user=user, data={'section': dict(section)})

    async def put(self, request, user, category_id):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        position = IntUtils.to_int(request.json.get('position'))

        category_id = IntUtils.to_int(category_id)
        if not category_id:
            return self.error(message='Отсуствует обязательный параметр "category_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.categories
            SET title = $2, photo = $3, position = $4
            WHERE id = $1
            RETURNING *
            ''',
            category_id,
            title,
            photo,
            position,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, category_id):
        category_id = IntUtils.to_int(category_id)
        if not category_id:
            return self.error(message='Отсуствует обязательный параметр "category_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.categories
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            category_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
