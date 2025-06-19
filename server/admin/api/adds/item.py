from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class AdView(BaseAPIView):

    async def get(self, request, user, ad_id):
        ad_id = IntUtils.to_int(ad_id)
        if not ad_id:
            return self.error(message='Отсуствует обязательный параметр "ad_id"')

        ad = await db.fetchrow(
            '''
            SELECT *
            FROM control.ads
            WHERE id = $1
            ''',
            ad_id
        ) or {}

        return self.success(request=request, user=user, data={'ad': dict(ad)})

    async def put(self, request, user, ad_id):
        title = StrUtils.to_str(request.json.get('title'))
        photo = StrUtils.to_str(request.json.get('photo'))
        position = IntUtils.to_int(request.json.get('position'))

        ad_id = IntUtils.to_int(ad_id)
        if not ad_id:
            return self.error(message='Отсуствует обязательный параметр "ad_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.ads
            SET title = $2, photo = $3, position = $4
            WHERE id = $1
            RETURNING *
            ''',
            ad_id,
            title,
            photo,
            position,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, ad_id):
        ad_id = IntUtils.to_int(ad_id)
        if not ad_id:
            return self.error(message='Отсуствует обязательный параметр "ad_id"')

        data = await db.fetchrow(
            '''
            UPDATE control.ads
            SET is_active = FALSE
            WHERE id = $1
            RETURNING *
            ''',
            ad_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
