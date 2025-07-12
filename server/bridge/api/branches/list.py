from datetime import datetime

from core.db import db
from core.handlers import TemplateHTTPView
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils

__all__ = [
    'BranchesBridgeView'
]

from utils.strs import StrUtils


class BranchesBridgeView(TemplateHTTPView):
    async def get(self, request):
        now = datetime.now()
        cond, cond_vars = ['is_active'], []

        query = StrUtils.to_str(request.args.get('query'))
        category_ids = StrUtils.to_str(request.args.get('category_ids'))
        category_ids = category_ids and ListUtils.to_list_of_ints(category_ids.split(','))
        branch_id = IntUtils.to_int(request.args.get('branch_id'))

        if query:
            cond.append('b.title ILIKE {}')
            cond_vars.append(f'%{query}%')

        if category_ids:
            cond.append('b.category_ids && {}')
            cond_vars.append(category_ids)

        if branch_id:
            cond.append('b.id = {}')
            cond_vars.append(branch_id)

        now_day = now.isoweekday()
        work_schedule_days = [now_day, now_day < 7 and now_day + 1 or 1]

        cond, _ = set_counters(' AND '.join(cond), counter=2)
        items = await db.fetch(
            '''
            SELECT
                b.id,
                b.title,
                b.photo,
                b.latitude,
                b.longitude,
                b.min_order_time,
                b.max_order_time,
                b.rating,
                b.promotion_text,
                b.phone,
                b.in_use,
                b.updated_at,
                b.created_at,
                b.min_order_sum,
                b.is_store,
                b.min_delivery_sum,
                (
                    SELECT JSON_AGG(JSONB_BUILD_OBJECT(
                        'id', c.id,
                        'title', c.title
                    ))
                    FROM control.categories c
                    WHERE id = ANY(b.category_ids)
                ) AS categories,
                (
                    SELECT JSON_AGG(JSONB_BUILD_OBJECT(
                        'day', w.day,
                        'started_at', w.started_at,
                        'stopped_at', w.stopped_at
                    ))
                    FROM control.work_schedule w
                    WHERE w.branch_id = b.id AND w.day = ANY ($1)
                ) AS work_schedule
            FROM control.branches b
            WHERE %s
            ORDER BY b.rating DESC
            ''' % cond,
            work_schedule_days,
            *cond_vars
        )

        branches = []
        for item in items:
            work_schedules = []
            if item.get('work_schedule'):
                work_schedules = sorted(item['work_schedule'], key=lambda x: x['day'])

            branches.append({
                **item,
                'work_schedule': work_schedules
            })

        if branch_id:
            return self.success(
                data={
                    'branch': branches[0] if branches else None
                }
            )

        return self.success(
            data={
                'branches': branches
            }
        )
