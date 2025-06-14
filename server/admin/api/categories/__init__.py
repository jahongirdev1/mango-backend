from sanic import Blueprint

from admin.api.categories.item import CategoryView
from admin.api.categories.list import CategoriesView

categories_bp = Blueprint('categories', url_prefix='/categories')

categories_bp.add_route(CategoriesView.as_view(), '/')
categories_bp.add_route(CategoryView.as_view(), '/<category_id>')
