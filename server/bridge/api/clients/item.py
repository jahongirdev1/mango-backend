from core.db import db
from core.handlers import TemplateHTTPView

from utils.phones import PhoneNumberUtils

from utils.strs import StrUtils

__all__ = [
    'ClientBridgeView'
]


class ClientBridgeView(TemplateHTTPView):
    async def get(self, request):
        phone = PhoneNumberUtils.normalize(request.json.get('phone'))
        if not phone:
            return self.error(message='Отсуствует обязательный параметры "Телефон номер"')

        uid = StrUtils.to_str(request.json.get('uid'))
        if not uid:
            return self.error(message='Отсуствует обязательный параметры "ХЭШ"')

        client = await db.fetchrow(
            '''
            SELECT id, name, photo, uid, phone
            FROM control.clients
            WHERE phone = $1
            ''',
            phone
        )

        if client and client['uid'] == uid:
            return self.success(data={
                'client': client
            })

        return self.error(message='Клиент не найден', status=401)
