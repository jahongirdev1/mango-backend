from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class WordView(BaseAPIView):

    async def get(self, request, user, word_id):
        word_id = IntUtils.to_int(word_id)
        if not word_id:
            return self.error(message='Отсуствует обязательный параметр "word_id"')

        item = await db.fetchrow(
            '''
            SELECT *
            FROM control.words
            WHERE id = $1
            ''',
            word_id
        ) or {}

        return self.success(request=request, user=user, data={'item': dict(item)})

    async def put(self, request, user, word_id):
        title = StrUtils.to_str(request.json.get('title'))

        word_id = IntUtils.to_int(word_id)
        if not word_id:
            return self.error(message='Отсуствует обязательный параметр "word_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.words
            SET title = $2
            WHERE id = $1
            RETURNING *
            ''',
            word_id,
            title
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, word_id):
        word_id = IntUtils.to_int(word_id)
        if not word_id:
            return self.error(message='Отсуствует обязательный параметр "word_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.words
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            word_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
