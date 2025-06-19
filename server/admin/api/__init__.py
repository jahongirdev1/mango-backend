from sanic import Blueprint

from admin.api.ads import ads_bp
from admin.api.branches import branches_bp
from admin.api.categories import categories_bp
from admin.api.clients import clients_bp
from admin.api.goods import goods_bp
from admin.api.main import MainView
from admin.api.profile import profile_bp
from admin.api.sections import sections_bp
from admin.api.users import users_bp
from admin.api.work_schedule import work_schedule_bp

main_bp = Blueprint('main', url_prefix='/')

main_bp.add_route(MainView.as_view(), '/')

api_group = Blueprint.group(
    main_bp,
    users_bp,
    clients_bp,
    profile_bp,
    sections_bp,
    branches_bp,
    categories_bp,
    goods_bp,
    work_schedule_bp,
    ads_bp,
    url_prefix='/api'
)
