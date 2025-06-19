from sanic import Blueprint

from admin.api.work_schedule.item import WorkScheduleItemView
from admin.api.work_schedule.list import WorkScheduleView

work_schedule_bp = Blueprint('work_schedule', url_prefix='/work-schedule')

work_schedule_bp.add_route(WorkScheduleView.as_view(), '/')
work_schedule_bp.add_route(WorkScheduleItemView.as_view(), '/<item_id>')
