from core.handlers import TemplateHTTPView
from utils.phones import PhoneNumberUtils

__all__ = [
    'PhoneValidationsBridgeView'
]


class PhoneValidationsBridgeView(TemplateHTTPView):
    async def get(self, request):
        query = PhoneNumberUtils.normalize(request.args.get('query'))
        return self.success(
            data={
                'is_valid': query and True or False
            }
        )
