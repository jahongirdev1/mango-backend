from sanic import Blueprint

from admin.api.adds.item import AdView
from admin.api.adds.list import AdsView

ads_bp = Blueprint('ads', url_prefix='/ads')

ads_bp.add_route(AdsView.as_view(), '/')
ads_bp.add_route(AdView.as_view(), '/<ad_id>')
