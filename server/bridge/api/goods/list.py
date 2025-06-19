from core.db import db
from core.handlers import TemplateHTTPView
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils
from utils.strs import StrUtils

__all__ = [
    'GoodsBridgeView'
]


class GoodsBridgeView(TemplateHTTPView):
    async def get(self, request):
        cond, cond_vars = ['g.is_active'], []
        branch_id = IntUtils.to_int(request.args.get('branch_id'))
        title = StrUtils.to_str(request.args.get('title'))

        if branch_id:
            cond.append('g.branch_id = {}')
            cond_vars.append(branch_id)

        if title:
            cond.append('g.title ILIKE {}')
            cond_vars.append(f'%{title}%')

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT
                g.id,
                g.title,
                g.price,
                g.description,
                g.photo,
                g.whole,
                g.is_new,
                g.in_use,
                g.balance,
                g.created_at,
                g.increment_step,
                g.discount_percent,
                (
                    CASE WHEN s.id IS NOT NULL THEN JSONB_BUILD_OBJECT(
                        'id', s.id,
                        'title', s.title,
                        'photo', s.photo,
                        'position', s.position
                    )
                    END
                ) AS section
            FROM control.goods g
            LEFT JOIN control.sections s ON g.section_id = s.id
            WHERE %s
            ''' % cond,
            *cond_vars
        ))

        return self.success(
            data={
                'goods': items
            }
        )
