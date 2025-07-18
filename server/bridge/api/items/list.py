from typing import Optional

from core.db import db
from core.handlers import TemplateHTTPView
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils

__all__ = [
    'ItemsBridgeView'
]


class ItemsBridgeView(TemplateHTTPView):
    @classmethod
    def calc_discount(cls, summ: float, promo_code: dict) -> tuple[bool, float, Optional[str]]:
        value = summ
        if not promo_code:
            return False, value, 'Промо-код не найден'

        if promo_code['in_use'] is False or promo_code['is_active'] is False:
            return False, value, 'Промо-код устарел'

        if promo_code['min_sum']:
            if value > promo_code['min_sum']:
                pass
            else:
                return False, value, f"Сумма меньше {promo_code['min_sum']}"

        if promo_code['max_sum']:
            if value < promo_code['max_sum']:
                pass
            else:
                return False, value, f"Сумма больше {promo_code['max_sum']}"

        if promo_code['percent']:
            value = value * (100 - promo_code['percent']) / 100

        if promo_code['discount_summ']:
            value = value - promo_code['discount_summ']

        value = value and value > 0 and value or 0

        return True, value, None

    async def get(self, request):
        uid = StrUtils.to_str(request.args.get('uid'))
        promocode_id = IntUtils.to_int(request.args.get('promocode_id'))

        if not uid:
            return self.error(message='Отсуствует обязательный параметр "uid"')

        items = await db.fetch(
            '''
            SELECT
                i.id,
                i.good_id,
                i.count,
                i.uid,
                g.title AS good_title,
                g.description AS good_description,
                g.discount_percent AS good_discount_percent,
                g.increment_step AS good_increment_step,
                g.balance AS good_balance,
                g.price AS good_price,
                g.photo AS good_photo,
                g.whole AS good_whole,
                g.branch_id AS good_branch_id
            FROM control.items i
            JOIN control.goods g ON i.good_id = g.id
            WHERE i.uid = $1
            ''',
            uid
        )

        data = []
        before_sum = 0
        for item in items:
            good_price = item['good_price']
            if good_price:
                if item['good_discount_percent']:
                    good_price = good_price * (100 - item['good_discount_percent']) / 100

            summ = good_price and good_price * item['count'] or 0
            before_sum += summ

            data.append({
                'id': item['id'],
                'good_id': item['good_id'],
                'count': item['count'],
                'uid': item['uid'],
                'good_title': item['good_title'],
                'good_description': item['good_description'],
                'good_discount_percent': item['good_discount_percent'],
                'good_increment_step': item['good_increment_step'],
                'good_price': item['good_price'],
                'good_photo': item['good_photo'],
                'good_whole': item['good_whole'],
                'good_balance': item['good_balance'],
                'good_branch_id': item['good_branch_id'],
                'sum': summ
            })

        after_sum = 0
        is_free_delivery = False
        if before_sum and promocode_id:
            promo_code = await db.fetchrow(
                '''
                SELECT is_active, in_use, percent, min_sum, max_sum, discount_summ, is_free_delivery
                FROM control.promocodes
                WHERE id = $1
                ''',
                promocode_id
            )
            if promo_code:
                is_free_delivery = promo_code['is_free_delivery']
                success, after_sum, error = self.calc_discount(before_sum, promo_code)
                if success is False:
                    return self.error(message=error)

        return self.success(
            data={
                'total_summ': after_sum,
                'before_sum': before_sum,
                'is_free_delivery': is_free_delivery,
                'items': data
            }
        )

    async def post(self, request):
        uid = StrUtils.to_str(request.json.get('uid'))
        if not uid:
            return self.error(message='Отсуствует обязательный параметр "uid"')

        good_id = IntUtils.to_int(request.json.get('good_id'))
        count = FloatUtils.to_float(request.json.get('count'), default=1)
        if good_id:
            good = await db.fetchrow(
                '''
                SELECT *
                FROM control.goods
                WHERE is_active AND in_use AND id = $1
                ''',
                good_id
            )
            if not good:
                return self.error(message='Товар не найден')

            if isinstance(good['balance'], int) and good['balance'] < count:
                return self.error(message='Товар не осталось в наличии')

        else:
            return self.error(message='Отсуствует обязательный параметр "good_id"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.items (good_id, uid, count)
            VALUES ($1, $2, $3)
            ON CONFLICT (good_id, uid) DO UPDATE SET count = excluded.count
            RETURNING id
            ''',
            good_id,
            uid,
            count
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request):
        uid = StrUtils.to_str(request.json.get('uid'))
        if not uid:
            return self.error(message='Отсуствует обязательный параметр "uid"')

        ids = ListUtils.to_list_of_ints(request.json.get('ids'))
        if not ids:
            return self.error(message='Отсуствует обязательный параметр "ids"')

        await db.execute(
            '''
            DELETE FROM control.items
            WHERE uid = $1 AND good_id = ANY ($2)
            RETURNING id
            ''',
            uid,
            ids
        )

        return self.success()
