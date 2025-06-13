from core.db import db
from core.handlers import TemplateHTTPView
from core.tools import set_counters
from utils.ints import IntUtils
from utils.lists import ListUtils

__all__ = [
    'SectionsBridgeView'
]


class SectionsBridgeView(TemplateHTTPView):
    async def get(self, request):
        cond, cond_vars = ['is_active'], []
        branch_id = IntUtils.to_int(request.args.get('branch_id'))
        if branch_id:
            cond.append('branch_id = {}')
            cond_vars.append(branch_id)

        cond, _ = set_counters(' AND '.join(cond))
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title, photo
            FROM control.sections
            WHERE %s
            ''' % cond,
            *cond_vars
        ))

        return self.success(
            data={
                'sections': items
            }
        )
