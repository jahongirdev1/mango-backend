import os

from sanic import Sanic
from sanic.exceptions import NotFound

from admin import admin_bp
from admin.api import api_group
from api.core.upload import UploadView
from bridge.api import bridge_bp
from core.auth import auth
from core.cache import cache
from core.db import mongo, db
from core.session import session
from exceptions import ExceptionsView
from settings import settings
from webhooks.telegram import TelegramWebhookView

app = Sanic(name='demo')

app.config.AUTH_LOGIN_URL = '/admin/login/'
app.config.ACCESS_LOG = False
app.config.DB_HOST = settings.get('db', {}).get('host', '127.0.0.1')
app.config.DB_DATABASE = settings.get('db', {}).get('database', 'maindb')
app.config.DB_PORT = settings.get('db', {}).get('port', 5432)
app.config.DB_USER = settings.get('db', {}).get('user', 'postgres')
app.config.DB_PASSWORD = settings.get('db', {}).get('password', '1234')
app.config.DB_POOL_MAX_SIZE = 25
app.config.RESPONSE_TIMEOUT = 600
app.config.FALLBACK_ERROR_FORMAT = 'html'
app.config.DEBUG = True
app.config['API_SCHEMES'] = ['https']
app.config['API_SECURITY'] = [{'ApiKeyAuth': []}]
app.config['API_SECURITY_DEFINITIONS'] = {
    'ApiKeyAuth': {'type': 'apiKey', 'in': 'header', 'name': 'X-API-Token'}
}


@app.listener('before_server_start')
async def initialize_modules(_app, _loop):
    await db.initialize(_app, _loop)
    mongo.initialize(_loop)
    await cache.initialize(_loop, maxsize=5)
    session.initialize(_app)
    auth.initialize(_app)


app.blueprint([
    api_group,
    admin_bp,
    bridge_bp
])

app.add_route(UploadView.as_view(), '/upload/')
app.add_route(TelegramWebhookView.as_view(), '/webhooks/telegram/')

app.error_handler.add(NotFound, ExceptionsView.instance().not_found)

app.static('/static', os.path.join(settings.get('file_path'), 'static'))

if __name__ == '__main__':
    try:
        app.run('127.0.0.1', port=8788, access_log=True, auto_reload=True)
    except Exception as e:
        print(e)
