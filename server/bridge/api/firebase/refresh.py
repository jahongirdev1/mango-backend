from core.db import db
from core.handlers import TemplateHTTPView
from utils.ints import IntUtils

from utils.strs import StrUtils

__all__ = [
    'RefreshFirebaseBridgeView'
]


class RefreshFirebaseBridgeView(TemplateHTTPView):
    async def post(self, request, client_id):
        client_id = IntUtils.to_int(client_id)
        if not client_id:
            return self.error(message='Отсуствует обязательный параметры "Клиент ID"')

        firebase_token = StrUtils.to_str(request.json.get('firebase_token'))
        if not firebase_token:
            return self.error(message='Отсуствует обязательный параметры "Токен"')

        updated_id = await db.fetchval(
            '''
            UPDATE control.clients
            SET firebase_token = $2
            WHERE id = $1
            RETURNING id
            ''',
            client_id,
            firebase_token
        )

        if not updated_id:
            return self.error(message='Операция не выполнена')

        return self.success()
