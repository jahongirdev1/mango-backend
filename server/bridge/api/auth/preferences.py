import traceback
from datetime import timedelta

import ujson

from api.core.base import BaseAPI
from core import errors
from core.partner import Partner
from modules import cache, db
from settings import settings
from utils.basic.ints import IntUtils
from utils.basic.lists import ListUtils


async def delete_preferences(app_id) -> bool:
    if app_id:
        await cache.delete(f'bridge:preferences:{app_id}')
        return True
    return False


async def get_preferences(app_id) -> dict:
    preferences = await cache.get(f'bridge:preferences:{app_id}')
    if preferences:
        return ujson.loads(preferences)

    _features = await db.fetch(
        '''
        SELECT bf.key
        FROM bridge.app_features AS baf
        LEFT JOIN bridge.features AS bf ON bf.id = baf.feature_id
        WHERE baf.app_id = $1 AND 'ui' = ANY(bf.scopes)
        ''',
        app_id,
        log=False
    )

    cross_interop_features = {
        'chat_bot': 'chatbot_enabled',
        'info_board': 'contact_sections_shown',
        'info_board_contacts': 'phones_list_shown',
        'p2p_audio_call': 'audio_call_enabled',
        'p2p_video_call': 'video_call_enabled',
        'services': 'services_enabled'
    }

    booleans = {booleans: False for booleans in cross_interop_features.values()}

    features = []
    for feature in _features:
        features.append(feature['key'])
        if feature['key'] in cross_interop_features:
            booleans[cross_interop_features[feature['key']]] = True

    contacts = ListUtils.to_list_of_dicts(await db.fetch(
        '''
        SELECT 
            wibs.id,
            i18n.get_translations_as_jsonb(wibs.title_id) AS title,
            i18n.get_translations_as_jsonb(wibs.description_id) AS description,
            (
                SELECT ARRAY_AGG(JSONB_BUILD_OBJECT(
                    'icon', wpn.icon,
                    'text', wpn.value,
                    'description', i18n.get_translations_as_jsonb(wpn.description_id),
                    'action', wpn.action
                ))
                FROM widget.info_board_phone_numbers AS wpn
                WHERE wpn.status >= 1 AND wpn.section_id = wibs.id
            ) AS items
        FROM widget.info_board_sections AS wibs
        WHERE wibs.status >= 1
        ORDER BY wibs.position
        ''',
        log=False
    )) or []

    try:
        if Partner.is_ecc():
            call_scopes = ListUtils.to_list_of_dicts(await db.fetch(
                '''
                SELECT *
                FROM public.widget_menus
                WHERE status > -1 AND app_id = $1
                ''',
                app_id,
                log=False
            ))
        else:
            call_scopes = ListUtils.to_list_of_dicts(await db.fetch(
                '''
                SELECT *
                FROM public.widget_menus
                WHERE status > -1
                ''',
                log=False
            ))

    except (Exception,):
        traceback.print_exc()
        call_scopes = None

    local_bot_configs = {**settings['project_settings']}
    for k, v in local_bot_configs['task_rating'].items():
        local_bot_configs['task_rating'][k]['title']['kz'] = v['title']['kk']

    configs = await db.fetchrow(
        '''
        SELECT * 
        FROM public.settings 
        WHERE app_id = $1
        ''',
        app_id,
        log=False
    )

    preferences = {
        'id': Partner.ID.value,
        'configs': configs['configs'] if configs else {},
        'contacts': configs['contacts'] if configs else {},
        'local_bot_configs': local_bot_configs,
        'info_blocks': contacts,
        'booleans': booleans,
        'call_scopes': call_scopes,
        'features': features
    }

    await cache.set(
        f'bridge:preferences:{app_id}',
        ujson.dumps(preferences),
        expire=int(timedelta(days=1).total_seconds())
    )

    return preferences


class BridgeAppPreferencesView(BaseAPI):

    async def get(self, request, app_id):
        app_id = IntUtils.to_int(app_id)
        if not app_id:
            return self.error(errors.RequiredField(field='app_id: int'))

        preferences = await get_preferences(app_id)

        return self.success(
            data=preferences
        )

    async def post(self, request, app_id):
        return self.error(errors.IllegalState())
