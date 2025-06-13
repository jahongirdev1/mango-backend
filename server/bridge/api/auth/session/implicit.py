import traceback
from datetime import timedelta

from aiohttp import BasicAuth

from api.core.base import BaseAPI
from bridge.public.api.auth.creds import set_auth_creds
from bridge.public.api.auth.preferences import get_preferences
from core import errors
from data.repository.bridge.sessions.repository import BridgeSessionsRepository
from modules import db
from utils.basic.dicts import DictUtils
from utils.basic.ints import IntUtils
from utils.basic.strs import StrUtils

__all__ = ['BridgeImplicitSessionView']


class BridgeImplicitSessionView(BaseAPI):

    async def get(self, request):
        return self.error(errors.IllegalState())

    async def post(self, request):
        authorization = StrUtils.to_str(request.headers.get('Authorization')) if request.headers else None
        if not authorization:
            return self.error(errors.PermissionDenied())

        try:
            decoded = BasicAuth.decode(authorization)
        except (Exception,):
            traceback.print_exc()
            return self.error(errors.PermissionDenied())

        client_id, client_secret = decoded.login, decoded.password

        app = await db.fetchrow(
            '''
            SELECT id, client_id, package, lifetime
            FROM bridge.apps 
            WHERE status >= 1 AND client_id = $1 AND client_secret = $2
            ''',
            client_id,
            client_secret
        )
        if not app:
            return self.error(errors.AppNotFound())

        success, _ = await set_auth_creds(
            app_id=app['id'],
            timeout=app['lifetime']
        )
        if not success:
            return self.error(errors.IllegalState())

        misc = {}
        if request.json:
            misc['ua'] = DictUtils.validate_dict(request.json.get('ua'))

            lang = StrUtils.to_str(request.json.get('lang'))
            misc['lang'] = lang if lang in ['en', 'kk', 'ru'] else None

            misc['customer_id'] = IntUtils.to_int(request.json.get('customer_id'))

        success, response = await BridgeSessionsRepository.generate_session(
            client_id=app['client_id'],
            app_id=app['id'],
            timeout=timedelta(minutes=20).total_seconds(),
            **misc
        )
        if success:
            preferences = None
            if app['package'] == 'full':
                preferences = await get_preferences(app['id'])

            return self.success(data={
                'creds': response,
                'preferences': preferences
            })

        return self.error(errors.OperationFailed())

    async def delete(self, request):
        access_token = request.args.get('access_token')
        if not access_token:
            return self.error(errors.RequiredField(field='access_token: str'))

        await BridgeSessionsRepository.delete_session(access_token)

        return self.success()
