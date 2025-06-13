import uuid
from datetime import timedelta
from typing import Optional, Tuple

from modules import cache


async def get_auth_creds(auth_token: str, field: str) -> Optional[dict]:
    if not auth_token or not field:
        return None
    value = await cache.hget(f'bridge:auth:{auth_token}', field)
    return value if value else None


async def set_auth_creds(app_id, timeout=None, **kwargs) -> Tuple[bool, dict]:
    auth_token, refresh_token = uuid.uuid4().hex, uuid.uuid4().hex

    expires_in = None
    if timeout:
        if timedelta(minutes=30).total_seconds() <= timeout <= timedelta(days=1).total_seconds():
            expires_in = timeout
    if not expires_in:
        expires_in = int(timedelta(minutes=30).total_seconds())

    transaction = cache.multi_exec()
    for k, v in {
        'app_id': app_id,
        'refresh_token': refresh_token,
        **kwargs
    }.items():
        if not v:
            continue
        transaction.hset(f'bridge:auth:{auth_token}', k, v)
    transaction.expire(f'bridge:auth:{auth_token}', expires_in)
    await transaction.execute()

    return True, {'auth_token': auth_token, 'refresh_token': refresh_token, 'expires_in': expires_in}
