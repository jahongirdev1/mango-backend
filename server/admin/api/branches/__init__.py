from sanic import Blueprint

from admin.api.branches.item import BranchView
from admin.api.branches.list import BranchesView

branches_bp = Blueprint('branches', url_prefix='/branches')

branches_bp.add_route(BranchesView.as_view(), '/')
branches_bp.add_route(BranchView.as_view(), '/<branch_id>')
