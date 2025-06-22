from core.db import db
from core.handlers import BaseAPIView
from core.tools import set_counters
from utils.bools import BoolUtils
from utils.floats import FloatUtils
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class GoodsView(BaseAPIView):
    template_name = 'admin/goods.html'

    async def get(self, request, user):
        branch_id = user['branch_id']
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        cond, cond_vars = ['is_active'], []
        section_id = IntUtils.to_int(request.args.get('section_id'))
        if section_id:
            cond.append('section_id = {}')
            cond_vars.append(section_id)

        if branch_id:
            cond.append('branch_id = {}')
            cond_vars.append(branch_id)

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT 
                id, 
                title, 
                price, 
                description, 
                photo, 
                whole, 
                is_new, 
                in_use, 
                is_active, 
                balance, 
                created_at, 
                increment_step,
                discount_percent
            FROM control.goods
            WHERE %s
            ORDER BY id DESC
            ''' % cond,
            *cond_vars
        ))

        return self.success(request=request, user=user, data={
            'goods': items
        })

    async def post(self, request, user):
        title = StrUtils.to_str(request.json.get('title'))
        price = FloatUtils.to_float(request.json.get('price'))
        description = StrUtils.to_str(request.json.get('description'))
        photo = StrUtils.to_str(request.json.get('photo'))
        whole = FloatUtils.to_float(request.json.get('whole'))
        is_new = BoolUtils.to_bool(request.json.get('is_new'))
        in_use = BoolUtils.to_bool(request.json.get('in_use'))
        balance = FloatUtils.to_float(request.json.get('balance'))
        discount_percent = FloatUtils.to_float(request.json.get('discount_percent'))
        section_id = IntUtils.to_int(request.json.get('section_id'))
        increment_step = FloatUtils.to_float(request.json.get('increment_step'))

        branch_id = user['branch_id']
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        if not section_id:
            return self.error(message='Отсуствует обязательный параметры "Секция"')

        if not title:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        if price and price < 0:
            return self.error(message='Не правильно ввели "Цену"')

        if balance and balance < 0:
            return self.error(message='Не правильно ввели "Остаток"')

        if whole and whole < 0:
            return self.error(message='Не правильно ввели "Весь"')

        if discount_percent and discount_percent < 0:
            return self.error(message='Не правильно ввели "Скидку"')

        if increment_step and increment_step < 0:
            return self.error(message='Не правильно ввели "шаг увеличения"')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.goods 
            (title, price, description, photo, whole, is_new, in_use, balance, branch_id, section_id, discount_percent,
             increment_step)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id
            ''',
            title,
            price,
            description,
            photo,
            whole,
            is_new,
            in_use,
            balance,
            branch_id,
            section_id,
            discount_percent,
            increment_step
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
