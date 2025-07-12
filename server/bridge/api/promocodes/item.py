from core.db import db
from core.handlers import TemplateHTTPView
from utils.ints import IntUtils
from utils.phones import PhoneNumberUtils

from utils.strs import StrUtils

__all__ = [
    'PromocodeBridgeView'
]


class PromocodeBridgeView(TemplateHTTPView):
    async def get(self, request, code):
        code = StrUtils.to_str(code)
        branch_id = IntUtils.to_int(request.args.get('branch_id'))
        phone = PhoneNumberUtils.normalize(request.args.get('phone'))

        if not code:
            return self.error(message='Отсуствует обязательный параметры "Код"')

        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        if not phone:
            return self.error(message='Отсуствует обязательный параметры "Телефон номер"')

        promocode = await db.fetchrow(
            '''
            SELECT id, title, code, is_active, in_use, created_at, percent, branch_id, min_sum, max_sum, discount_summ, "limit", description, is_disposable, is_free_delivery
            FROM control.promocodes
            WHERE code = $1 AND (branch_id = $2 OR branch_id IS NULL)
            ''',
            code,
            branch_id
        )

        if not promocode or promocode['is_active'] is False:
            return self.success(
                data={
                    'is_valid': False,
                    'message': 'Промокод не найден'
                }
            )

        if promocode['in_use'] is False:
            return self.success(
                data={
                    'is_valid': False,
                    'message': 'Устаревший прокод'
                }
            )

        if promocode['limit'] is not None:
            pass

        return self.success(
            data={
                'is_valid': True,
                'promocode': dict(promocode),
            }
        )
