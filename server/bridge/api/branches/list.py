from datetime import datetime

from core.db import db
from core.handlers import TemplateHTTPView
from core.tools import set_counters
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

        if query:
            cond.append('b.title ILIKE {}')
            cond_vars.append(f'%{query}%')

        if category_ids:
            cond.append('b.category_ids && {}')
            cond_vars.append(category_ids)

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
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
                        'started_at', w.started_at,
                        'stopped_at', w.stopped_at
                    ))
                    FROM control.work_schedule w
                    WHERE w.branch_id = b.id
                ) AS work_schedule
            FROM control.branches b
            WHERE %s
            ORDER BY b.rating DESC
            ''' % cond,
            *cond_vars
        ))

        return self.success(
            data={
                'branches': items
            }
        )
