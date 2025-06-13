from api.core.base import BaseAPI
from bridge.public.api.auth.creds import set_auth_creds
from bridge.public.api.auth.preferences import get_preferences
from core import errors
from modules import db
from utils.basic.strs import StrUtils

__all__ = ['BridgeAuthView']


class BridgeAuthView(BaseAPI):

    async def get(self, _):
        return self.error(errors.IllegalState())

    async def post(self, request):
        if not request.json:
            return self.error(errors.RequiredParams())

        client_id = StrUtils.to_str(request.json.get('client_id'), default='web-widget')
        client_secret = StrUtils.to_str(request.json.get('client_secret'))

        app = await db.fetchrow(
            '''
            SELECT id, client_id, package, lifetime
            FROM bridge.apps 
            WHERE status >= 1 AND client_id = $1 AND COALESCE(client_secret, 'undefined') = $2
            ''',
            client_id,
            client_secret or 'undefined',
            log=False
        )
        if not app:
            return self.error(errors.AppNotFound())

        success, response = await set_auth_creds(
            app_id=app['id'],
            timeout=app['lifetime']
        )
        if not success:
            return self.error(errors.IllegalState())

        if app['package'] == 'full':
            return self.success(
                creds=response,
                data=await get_preferences(app['id'])
            )

        return self.success(creds=response)
