from core.handlers import TemplateHTTPView
from utils.phones import PhoneNumberUtils

__all__ = [
    'PhoneValidationsBridgeView'
]


class PhoneValidationsBridgeView(TemplateHTTPView):
    async def get(self, request, code):
        phone = PhoneNumberUtils.normalize(request.args.get('phone'))
        return self.success(
            data={
                'is_valid': phone and True or False
            }
        )
