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
            SELECT id, name, photo, uid, phone
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

        name = StrUtils.to_str(request.json.get('name'))
        photo = StrUtils.to_str(request.json.get('photo'))
        latitude = FloatUtils.to_float(request.json.get('latitude'))
        longitude = FloatUtils.to_float(request.json.get('longitude'))

        client = await db.fetchrow(
            '''
            UPDATE control.clients
            SET name = $3, photo = $4, latitude = $5, longitude = $6
            WHERE uid = $1 AND phone = $2
            RETURNING *
            ''',
            uid,
            phone,
            name,
            photo,
            latitude,
            longitude
        )

        if not client:
            return self.error(message='Операция не выполнена')

        return self.success(data={
            'client': dict(client)
        })
