from bridge.public.api.auth.creds import get_auth_creds
from modules import db
from utils.basic.ints import IntUtils
from utils.basic.lists import ListUtils
from utils.result import AnyResult, Result


async def get_specs(app_id) -> AnyResult:
    features = ListUtils.to_list_of_dicts(await db.fetch(
        '''
        SELECT bf.key, bf.title
        FROM bridge.features AS bf 
        LEFT JOIN bridge.app_features AS baf ON baf.feature_id = bf.id 
        WHERE baf.app_id = $1
        ''',
        app_id
    ))

    calls = ListUtils.to_list_of_dicts(await db.fetch(
        '''
        SELECT cq.code AS topic, bs.call_type
        FROM calls.queues AS cq
        LEFT JOIN bridge.settings_calls_p2p AS bs ON bs.topic_id = cq.id 
        WHERE bs.app_id = $1
        ''',
        app_id
    ))

    return Result.Success({
        'app_id': app_id,
        'features': features,
        'calls': calls
    })


async def check_permission(action=None, data=None, call_type=None, topic=None, token=None) -> bool:
    if token and not data:
        app_id = IntUtils.to_int(await get_auth_creds(token, 'app_id'))
        if app_id:
            result = await get_specs(app_id)
        else:
            return False

        if isinstance(result, Result.Success):
            data = result.data

    if action and data:
        if action == 'p2p_video_call':
            is_feature_enabled = False
            is_topic_enabled = False

            for feature in data.get('features', []):
                if feature['key'] == action:
                    is_feature_enabled = True
                    break

            for call in data.get('calls', []):
                if call['topic'] == topic and call['call_type'] == call_type:
                    is_topic_enabled = True
                    break

            if is_feature_enabled and is_topic_enabled:
                return True

    return False
