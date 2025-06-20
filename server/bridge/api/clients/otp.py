import ujson

from core.cache import cache
from core.db import db
from core.handlers import TemplateHTTPView
from utils.phones import PhoneNumberUtils
from utils.strs import StrUtils

__all__ = [
    'OtpClientBridgeView'
]


class OtpClientBridgeView(TemplateHTTPView):
    @classmethod
    def generate_opt(cls):
        # return "".join(random.choices("0123456789", k=6))
        return '123456'

    async def post(self, request, action):
        action = StrUtils.to_str(action)
        if not action:
            return self.error(message='Отсуствует обязательный параметры "action"')

        phone = PhoneNumberUtils.normalize(request.json.get('phone'))
        if not phone:
            return self.error(message='Отсуствует обязательный параметры "Телефон номер"')

        if action == 'generate':
            uid = StrUtils.to_str(request.json.get('uid'))
            if not uid:
                return self.error(message='Отсуствует обязательный параметры "ХЭШ"')

            await cache.set(f'mango:opt:{phone}', ujson.dumps({
                'uid': uid,
                'otp': self.generate_opt()
            }), expire=60 * 10)

            return self.success()

        elif action == 'check':
            otp = StrUtils.to_str(request.json.get('otp'))
            if not otp:
                return self.error(message='Отсуствует обязательный параметры "Код"')

            item = await cache.get(f'mango:opt:{phone}')
            if item:
                item = ujson.loads(item)
                if item['otp'] == otp:
                    client = await db.fetchrow(
                        '''
                        INSERT INTO control.clients (uid, phone)
                        VALUES ($1, $2)
                        ON CONFLICT (phone) DO UPDATE SET uid = excluded.uid
                        RETURNING id, last_name, first_name, photo, uid, phone
                        ''',
                        item['uid'],
                        phone,
                    ) or {}

                    return self.success(data={'client': dict(client)})

                return self.error(message='Введен неверный OTP. Пожалуйста, проверьте код и попробуйте снова')

            return self.error(message='Срок действия введенного OTP истёк. Пожалуйста, запросите новый код')

        return self.error(message='Операция не выполнена')
