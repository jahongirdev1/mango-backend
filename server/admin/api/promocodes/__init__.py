from sanic import Blueprint

from admin.api.promocodes.item import PromocodeView
from admin.api.promocodes.list import PromocodesView

promocodes_bp = Blueprint('promocodes', url_prefix='/promocodes')

promocodes_bp.add_route(PromocodesView.as_view(), '/')
promocodes_bp.add_route(PromocodeView.as_view(), '/<promocode_id>')
