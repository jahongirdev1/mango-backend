import traceback

import asyncpg

from core.datetimes import DatetimeUtils
from core.db import db
from core.handlers import BaseAPIView
from core.hasher import password_to_hash
from core.pager import Pager
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.phones import PhoneNumberUtils
from utils.strs import StrUtils


class UsersListView(BaseAPIView):
    template_name = 'admin/users.html'

    async def get(self, request, user):
        pager = Pager()
        pager.set_page(request.args.get('page', 1))
        pager.set_limit(request.args.get('limit', 50))

        query = StrUtils.to_str(request.args.get('query'))
        status = IntUtils.to_int(request.args.get('status'))

        cond, cond_vars = ['is_active'], []

        if query:
            cond.append('(u.first_name ILIKE {} OR u.last_name ILIKE {})')
            cond_vars.append(f'%{query}%')
            cond_vars.append(f'%{query}%')

        if status is not None:
            cond.append('u.status = {}')
            cond_vars.append(status)
        else:
            cond.append('u.status = {}')
            cond_vars.append(0)

        if user['branch_id']:
            cond.append('u.branch_id = {}')
            cond_vars.append(user['branch_id'])

        cond, _ = set_counters(' AND '.join(cond))

        users = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT u.*
            FROM public.users u
            WHERE %s
            ORDER BY id DESC
            %s
            ''' % (cond, pager.as_query()),
            *cond_vars
        ))

        pager.set_total(await db.fetchval(
            '''
            SELECT count(*)
            FROM public.users u
            WHERE %s
            ''' % cond,
            *cond_vars
        ) or 0)

        return self.success(request=request, user=user, data={
            '_success': True,
            'users': users,
            'pager': pager.dict()
        })

    async def post(self, request, user):
        first_name = StrUtils.to_str(request.json.get('first_name'))
        last_name = StrUtils.to_str(request.json.get('last_name'))
        middle_name = StrUtils.to_str(request.json.get('middle_name'))
        birthday = DatetimeUtils.parse(request.json.get('birthday'))
        username = StrUtils.to_str(request.json.get('username'))
        password = StrUtils.to_str(request.json.get('password'))
        role_id = IntUtils.to_int(request.json.get('role_id'))
        photo = StrUtils.to_str(request.json.get('photo'))
        branch_id = IntUtils.to_int(user['branch_id'] or request.json.get('branch_id'))
        phone = PhoneNumberUtils.normalize(request.json.get('phone'))

        if not first_name:
            return self.error(message='Отсуствует обязательный параметры "Имя"')

        if not username:
            return self.error(message='Отсуствует обязательный параметр "Логин"')

        if not password:
            return self.error(message='Отсуствует обязательный параметр "Пароль"')

        try:
            user = await db.fetchrow(
                '''
                INSERT INTO public.users
                (last_name, first_name, middle_name, password, username, photo, birthday, role_id, branch_id, phone)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING *
                ''',
                last_name,
                first_name,
                middle_name,
                password_to_hash(password),
                username,
                photo,
                birthday,
                role_id,
                branch_id,
                phone
            )

        except asyncpg.exceptions.UniqueViolationError:
            traceback.print_exc()
            return self.error(
                message='Пользователь с этими значениями уже существует. Дубликат не может быть создан'
            )

        if not user:
            return self.error(message='Операция не выполнена')

        return self.success(data={'user': dict(user)})
