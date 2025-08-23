from core.db import mongo
from core.handlers import BaseAPIView
from core.pager import Pager
from utils.ints import IntUtils
from utils.strs import StrUtils


class OrdersView(BaseAPIView):

    async def get(self, request, user):
        branch_id = user['branch_id']

        filters = {
            'is_active': True
        }

        status = StrUtils.to_str(request.args.get('status'))
        if status:
            filters['status'] = status

        if branch_id:
            filters['branch_id'] = branch_id

        limit = request.args.get('limit', 100)

        pager = Pager()
        pager.set_page(request.args.get('page', 1))
        pager.set_limit(limit + 1)
        offset = IntUtils.to_int(request.args.get('offset')) or pager.offset

        items = await mongo.orders.find(filters).skip(offset) \
            .limit(pager.limit) \
            .sort('_id', -1) \
            .to_list(length=None)

        return self.success(request=request, user=user, data={
            'orders': items[:limit],
            'has_next': True if len(items) > limit else False
        })
