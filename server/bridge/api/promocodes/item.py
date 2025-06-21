from core.db import db
from core.handlers import TemplateHTTPView
from utils.ints import IntUtils

from utils.strs import StrUtils

__all__ = [
    'PromocodeBridgeView'
]


class PromocodeBridgeView(TemplateHTTPView):
    async def get(self, request, code):
        code = StrUtils.to_str(code)
        branch_id = IntUtils.to_int(request.args.get('branch_id'))

        if not code:
            return self.error(message='Промокод не найден')

        if not branch_id:
            return self.error(message='Промокод не найден')

        val = await db.fetchval(
            '''
            SELECT id
            FROM control.promocodes
            WHERE is_active AND in_use AND code = $1 AND (branch_id = $2 OR branch_id IS NULL)
            ''',
            code,
            branch_id
        ) and True or False

        return self.success(
            data={
                'is_valid': val
            }
        )
