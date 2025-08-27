from core.handlers import TemplateHTTPView

__all__ = [
    'VersionBridgeView'
]


class VersionBridgeView(TemplateHTTPView):
    async def get(self, request):
        return self.success(
            data={
                'version': '5.2',
                'is_required': True
            }
        )
