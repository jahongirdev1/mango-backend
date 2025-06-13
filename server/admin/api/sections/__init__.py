from sanic import Blueprint

from admin.api.sections.item import SectionView
from admin.api.sections.list import SectionsView

sections_bp = Blueprint('sections', url_prefix='/sections')

sections_bp.add_route(SectionsView.as_view(), '/')
sections_bp.add_route(SectionView.as_view(), '/<section_id>')
