from datetime import timedelta

from timber import Timber

from api.core.base import BaseAPI
from bridge.public.api.auth.creds import get_auth_creds
from core import errors
from data.repository.bridge.sessions.repository import BridgeSessionsRepository
from data.repository.customers.repository import CustomersRepository
from modules import db
from utils.basic.dicts import DictUtils
from utils.basic.iin import IIN
from utils.basic.ints import IntUtils
from utils.basic.strs import StrUtils

__all__ = ['BridgeExplicitSessionView']

timber = Timber(__name__)


class BridgeExplicitSessionView(BaseAPI):

    async def get(self, _):
        return self.error(errors.IllegalState())

    async def post(self, request):
        auth_token = request.args.get('auth_token')
        if not auth_token:
            return self.error(errors.RequiredField(field='auth_token: str'))

        app_id = IntUtils.to_int(await get_auth_creds(auth_token, 'app_id'))
        if not app_id:
            return self.error(errors.AuthCredsNotFound())

        app = await db.fetchrow(
            '''
            SELECT id, client_id
            FROM bridge.apps
            WHERE status >= 1 AND id = $1
            ''',
            app_id,
            log=False
        )
        if not app:
            return self.error(errors.AppNotFound())

        params = request.json or {}
        misc = {}
        if params:
            misc['origin'] = StrUtils.to_str(params.get('origin'))

            misc['ua'] = DictUtils.validate_dict(params.get('ua'))

            lang = StrUtils.to_str(params.get('lang'))
            misc['lang'] = lang if lang in ['en', 'kk', 'ru'] else None

            customer = {}

            for k in ['first_name', 'last_name', 'patronymic', 'iin', 'email', 'phone_number']:
                if k == 'iin':
                    iin = IIN.of(params.get('iin'))
                    v = iin.value if iin else None
                else:
                    v = StrUtils.to_str(params.get(k))

                if v:
                    customer[k] = v

            if customer:
                c_success, c_response = await CustomersRepository.instance().upsert(
                    origin='bridge',
                    params={
                        'first_name': customer.get('first_name'),
                        'last_name': customer.get('last_name'),
                        'patronymic': customer.get('patronymic'),
                        'iin': customer.get('iin'),
                        'email': customer.get('email'),
                        'phone': customer.get('phone_number'),
                    }
                )
                if c_success:
                    misc['user_id'] = c_response['id']

            # timber.d(f'BridgeExplicitSessionView#post() -> client_id: {app["client_id"]}, params: {params}, misc:{misc}')

        success, response = await BridgeSessionsRepository.generate_session(
            client_id=app['client_id'],
            app_id=app['id'],
            timeout=timedelta(minutes=20).total_seconds(),
            **misc
        )
        if success:
            return self.success(data=response)

        return self.error(errors.OperationFailed())

    async def delete(self, request):
        access_token = request.args.get('access_token')
        if not access_token:
            return self.error(errors.RequiredField(field='access_token: str'))

        await BridgeSessionsRepository.delete_session(access_token)

        return self.success()
