from core.db import db
from core.handlers import BaseAPIView
from core.tools import set_counters
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class PromocodesView(BaseAPIView):
    template_name = 'admin/promocodes.html'

    async def get(self, request, user):
        branch_id = user['branch_id']

        cond, cond_vars = ['is_active'], []
        if branch_id:
            cond.append('branch_id = {}')
            cond_vars.append(branch_id)

        query = StrUtils.to_str(request.args.get('query'))
        if query:
            cond.append('(title ILIKE {same} OR code ILIKE {})')
            cond_vars.append(f'%{query}%')

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT *
            FROM control.promocodes
            WHERE %s
            ORDER BY id DESC
            ''' % cond,
            *cond_vars
        ))

        return self.success(request=request, user=user, data={
            'promocodes': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        code = StrUtils.to_str(request.json.get('code'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        percent = IntUtils.to_int(request.json.get('percent'))
        min_sum = FloatUtils.to_float(request.json.get('min_sum'))
        max_sum = FloatUtils.to_float(request.json.get('max_sum'))
        discount_summ = FloatUtils.to_float(request.json.get('summ'))
        limit = IntUtils.to_int(request.json.get('limit'))
        branch_id = IntUtils.to_int(request.json.get('branch_id'))
        description = StrUtils.to_str(request.json.get('description'))
        is_disposable = BoolUtils.to_bool(request.json.get('is_disposable'))
        is_free_delivery = BoolUtils.to_bool(request.json.get('is_free_delivery'))

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        if not code:
            return self.error(message='Отсуствует обязательный параметры "Код"')

        print('limit', limit)

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.promocodes (title, code, in_use, branch_id, percent, min_sum, max_sum, limit, description, discount_summ, is_disposable, is_free_delivery)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            ''',
            title,
            code,
            in_use,
            branch_id,
            percent,
            min_sum,
            max_sum,
            limit,
            description,
            discount_summ,
            is_disposable,
            is_free_delivery
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
