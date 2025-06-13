from core.db import db
from core.handlers import TemplateHTTPView

from utils.strs import StrUtils

__all__ = [
    'PromocodeBridgeView'
]


class PromocodeBridgeView(TemplateHTTPView):
    async def get(self, request, code):
        code = StrUtils.to_str(code)
        if not code:
            return self.error(message='Промокод не найден')

        val = await db.fetchval(
            '''
            SELECT id
            FROM control.promocodes
            WHERE is_active and in_use AND code = $1
            ''',
            code
        ) and True or False

        return self.success(
            data={
                'is_valid': val
            }
        )
