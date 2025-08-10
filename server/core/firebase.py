import traceback

import firebase_admin
from firebase_admin import credentials, messaging

from settings import settings


class Firebase:
    @classmethod
    def initialize(cls):
        cred = credentials.Certificate(settings.get('file_path', '') + '/static/firebase_config.json')
        firebase_admin.initialize_app(cred)

    @classmethod
    def send_message(cls, token: str, data: dict):
        try:
            message = messaging.Message(
                token=token,
                data=data
            )
            print(f'Firebase#send_message() -> token: {token}, data: {data}')
            print(messaging.send(message))
        except (Exception,):
            traceback.print_exc()
