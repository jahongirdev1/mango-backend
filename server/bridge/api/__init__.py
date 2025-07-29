from sanic import Blueprint

from bridge.api.ads.list import AdsListView
from bridge.api.branches.list import BranchesBridgeView
from bridge.api.categories.list import CategoriesBridgeView
from bridge.api.clients.item import ClientBridgeView
from bridge.api.clients.otp import OtpClientBridgeView
from bridge.api.goods.list import GoodsBridgeView
from bridge.api.items.calc import CalcBridgeView
from bridge.api.items.list import ItemsBridgeView
from bridge.api.promocodes.item import PromocodeBridgeView
from bridge.api.sections.list import SectionsBridgeView
from bridge.api.validations.phone import PhoneValidationsBridgeView
from bridge.api.words.list import WordsBridgeView

__all__ = ['bridge_bp']

_api_bp = Blueprint('bridge-api', url_prefix='api')

_api_bp.add_route(AdsListView.as_view(), '/ads/')
_api_bp.add_route(CategoriesBridgeView.as_view(), '/categories/')
_api_bp.add_route(BranchesBridgeView.as_view(), '/branches/')
_api_bp.add_route(SectionsBridgeView.as_view(), '/sections/')
_api_bp.add_route(GoodsBridgeView.as_view(), '/goods/')
_api_bp.add_route(PromocodeBridgeView.as_view(), '/promocodes/<code>/')
_api_bp.add_route(ClientBridgeView.as_view(), '/client/')
_api_bp.add_route(ItemsBridgeView.as_view(), '/items/')
_api_bp.add_route(CalcBridgeView.as_view(), '/calc/')
_api_bp.add_route(OtpClientBridgeView.as_view(), '/client/otp/<action>/')
_api_bp.add_route(PhoneValidationsBridgeView.as_view(), '/validations/phone/')
_api_bp.add_route(WordsBridgeView.as_view(), '/words/')

bridge_bp = Blueprint.group(
    _api_bp,
    url_prefix='/bridge'
)
