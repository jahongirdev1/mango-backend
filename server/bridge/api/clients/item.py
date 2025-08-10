from core.db import db
from core.handlers import TemplateHTTPView
from utils.floats import FloatUtils

from utils.phones import PhoneNumberUtils

from utils.strs import StrUtils

__all__ = [
    'ClientBridgeView'
]


class ClientBridgeView(TemplateHTTPView):
    async def get(self, request):
        phone = PhoneNumberUtils.normalize(request.args.get('phone'))
        if not phone:
            return self.error(message='Отсуствует обязательный параметры "Телефон номер"')

        uid = StrUtils.to_str(request.args.get('uid'))
        if not uid:
            return self.error(message='Отсуствует обязательный параметры "ХЭШ"')

        client = await db.fetchrow(
            '''
            SELECT id, first_name, last_name, photo, uid, phone, has_admin
            FROM control.clients
            WHERE phone = $1
            ''',
            phone
        )

        if client and client['uid'] == uid:
            return self.success(data={
                'client': dict(client)
            })

        return self.error(message='Клиент не найден', status=401)

    async def post(self, request):
        phone = PhoneNumberUtils.normalize(request.json.get('phone'))
        if not phone:
            return self.error(message='Отсуствует обязательный параметры "Телефон номер"')

        uid = StrUtils.to_str(request.json.get('uid'))
        if not uid:
            return self.error(message='Отсуствует обязательный параметры "ХЭШ"')

        first_name = StrUtils.to_str(request.json.get('first_name'))
        last_name = StrUtils.to_str(request.json.get('last_name'))
        photo = StrUtils.to_str(request.json.get('photo'))
        latitude = FloatUtils.to_float(request.json.get('latitude'))
        longitude = FloatUtils.to_float(request.json.get('longitude'))

        client = await db.fetchrow(
            '''
            UPDATE control.clients
            SET first_name = $3, last_name = $4, photo = $5, latitude = $6, longitude = $7
            WHERE uid = $1 AND phone = $2
            RETURNING *
            ''',
            uid,
            phone,
            first_name,
            last_name,
            photo,
            latitude,
            longitude
        )

        if not client:
            return self.error(message='Операция не выполнена')

        return self.success(data={
            'client': dict(client)
        })
