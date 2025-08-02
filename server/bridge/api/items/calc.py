import math
from typing import Optional

from core.db import db
from core.handlers import TemplateHTTPView
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.strs import StrUtils

__all__ = [
    'CalcBridgeView'
]


class CalcBridgeView(TemplateHTTPView):

    @classmethod
    def haversine(cls, lat1, lon1, lat2, lon2):
        R = 6371.0

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

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
        branch_id = IntUtils.to_int(request.args.get('branch_id'))
        latitude = FloatUtils.to_float(request.args.get('latitude'))
        longitude = FloatUtils.to_float(request.args.get('longitude'))

        if not uid:
            return self.error(message='Отсуствует обязательный параметр "uid"')

        if not branch_id:
            return self.error(message='Отсуствует обязательный параметр "branch_id"')

        if not latitude:
            return self.error(message='Отсуствует обязательный параметр "latitude"')

        if not longitude:
            return self.error(message='Отсуствует обязательный параметр "longitude"')

        delivery = 0

        branch = await db.fetchrow(
            '''
            SELECT *
            FROM control.branches
            WHERE id = $1
            ''',
            branch_id
        )
        if not branch or branch['is_active'] is False:
            return self.error(message='Операция не выполнена')

        if branch['min_delivery_sum'] and branch['latitude'] and branch['longitude']:
            distance_km = self.haversine(branch['latitude'], branch['longitude'], latitude, longitude)
            delivery = distance_km and distance_km * branch['min_delivery_sum'] or 0

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
        summary = 0
        for item in items:
            good_price = item['good_price']
            if good_price:
                if item['good_discount_percent']:
                    good_price = good_price * (100 - item['good_discount_percent']) / 100

            summ = good_price and good_price * item['count'] or 0
            summary += summ

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

        promo_discount = 0
        error = str()
        if summary and promocode_id:
            promo_code = await db.fetchrow(
                '''
                SELECT is_active, in_use, percent, min_sum, max_sum, discount_summ, is_free_delivery
                FROM control.promocodes
                WHERE id = $1
                ''',
                promocode_id
            )
            if promo_code:
                if promo_code['is_free_delivery']:
                    delivery = 0

                success, after_sum, error = self.calc_discount(summary, promo_code)
                if success is True:
                    promo_discount = summary > after_sum and summary - after_sum or summary

        service_cost = 10
        return self.success(
            data={
                'promo_discount': promo_discount,
                'summary': summary,
                'service': ((summary - promo_discount) + delivery) * service_cost / 100,
                'delivery': delivery,
                'total': ((summary - promo_discount) + delivery) * (service_cost + 100) / 100,
                'error': error
            }
        )
