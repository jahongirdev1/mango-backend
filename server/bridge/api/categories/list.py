from core.db import db
from core.handlers import TemplateHTTPView
from utils.lists import ListUtils

__all__ = [
    'CategoriesBridgeView'
]


class CategoriesBridgeView(TemplateHTTPView):
    async def get(self, request):
        items = ListUtils.to_list_of_dicts(await db.fetch(
            '''
            SELECT id, title, photo, position
            FROM control.categories
            WHERE is_active 
            '''
        ))
        return self.success(
            data={
                'categories': items
            }
        )
