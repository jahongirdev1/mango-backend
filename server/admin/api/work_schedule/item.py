from datetime import datetime

from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.strs import StrUtils


class WorkScheduleItemView(BaseAPIView):

    async def get(self, request, user, item_id):
        item_id = IntUtils.to_int(item_id)
        if not item_id:
            return self.error(message='Отсуствует обязательный параметр "item_id"')

        item = await db.fetchrow(
            '''
            SELECT *
            FROM control.work_schedule
            WHERE id = $1
            ''',
            item_id
        ) or {}

        return self.success(request=request, user=user, data={'item': dict(item)})

    async def put(self, request, user, item_id):
        day = IntUtils.to_int(request.json.get('day'))
        if not day:
            return self.error(message='Отсуствует обязательный параметры "День"')

        started_at = StrUtils.to_str(request.json.get('started_at'))
        if started_at:
            started_at = datetime.strptime(started_at[:5], '%H:%M')
        else:
            return self.error(message='Отсуствует обязательный параметры "Время начало"')

        stopped_at = StrUtils.to_str(request.json.get('stopped_at'))
        if stopped_at:
            stopped_at = datetime.strptime(stopped_at[:5], '%H:%M')
        else:
            return self.error(message='Отсуствует обязательный параметры "Время конца"')

        item_id = IntUtils.to_int(item_id)
        if not item_id:
            return self.error(message='Отсуствует обязательный параметр "item_id"')

        if started_at >= stopped_at:
            return self.error(message='Отсуствует обязательный параметры')

        data = await db.fetchrow(
            '''
            UPDATE control.work_schedule
            SET day = $2, started_at = $3, stopped_at = $4
            WHERE id = $1
            RETURNING *
            ''',
            item_id,
            day,
            started_at,
            stopped_at,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()

    async def delete(self, request, user, item_id):
        item_id = IntUtils.to_int(item_id)
        if not item_id:
            return self.error(message='Отсуствует обязательный параметр "item_id"')

        data = await db.fetchrow(
            '''
            DELETE FROM control.work_schedule
            WHERE id = $1
            RETURNING *
            ''',
            item_id,
        )

        if not data:
            return self.error(message='Операция не выполнена')

        return self.success()
