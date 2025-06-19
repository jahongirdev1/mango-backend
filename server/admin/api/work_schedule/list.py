from datetime import datetime

from core.db import db
from core.handlers import BaseAPIView
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils


class WorkScheduleView(BaseAPIView):
    DAYS = {
        1: "Понедельник",
        2: "Вторник",
        3: "Среда",
        4: "Четверг",
        5: "Пятница",
        6: "Суббота",
        7: "Воскресенье"
    }
    template_name = 'admin/work-schedule.html'

    async def get(self, request, user):
        branch_id = user['branch_id']

        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        items = await db.fetch(
            '''
            SELECT id, branch_id, day, started_at, stopped_at
            FROM control.work_schedule
            WHERE branch_id = $1
            ORDER BY day DESC
            ''',
            branch_id
        )

        data = []
        for item in items:
            data.append({
                'id': item['id'],
                'day_title': self.DAYS[item['day']],
                'day': item['day'],
                'started_at': item['started_at'],
                'stopped_at': item['stopped_at']
            })

        return self.success(request=request, user=user, data={
            'items': data
        })

    async def post(self, request, user):
        branch_id = user['branch_id']
        if not branch_id:
            return self.error(message='Отсуствует обязательный параметры "Филиал"')

        day = IntUtils.to_int(request.json.get('day'))
        if not day:
            return self.error(message='Отсуствует обязательный параметры "День"')

        started_at = StrUtils.to_str(request.json.get('started_at'))
        if started_at:
            started_at = datetime.strptime(started_at, '%H:%M')
        else:
            return self.error(message='Отсуствует обязательный параметры "Время начало"')

        stopped_at = StrUtils.to_str(request.json.get('stopped_at'))
        if stopped_at:
            stopped_at = datetime.strptime(stopped_at, '%H:%M')
        else:
            return self.error(message='Отсуствует обязательный параметры "Время конца"')

        if started_at >= stopped_at:
            return self.error(message='Отсуствует обязательный параметры')

        inserted_id = await db.fetchval(
            '''
            INSERT INTO control.work_schedule (branch_id, day, started_at, stopped_at)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            ''',
            branch_id,
            day,
            started_at.time(),
            stopped_at.time()
        )

        if not inserted_id:
            return self.error(message='Операция не выполнена')

        return self.success(data={})
