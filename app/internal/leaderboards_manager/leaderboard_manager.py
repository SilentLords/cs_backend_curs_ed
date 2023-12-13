from app.configuration.settings import settings
from app.internal.utils.schemas import T
from app.internal.utils.services import fetch_data_from_external_api, collect_base_statistics
from typing import Tuple


async def get_all_leaderboard_data_from_external_api(offset: int = 0, limit: int = 20) -> Tuple[bool, T]:
    q_param = {'offset': offset, "limit": limit}
    leaderboards_data = await fetch_data_from_external_api(q_param=q_param,
                                                           path=f'leaderboards/hubs/8a9629cf-c837-4389-97a1-1c47cf886df4')

    if leaderboards_data:

        all_leaderboards_data = []
        for leaderboard in leaderboards_data['items']:
            leaderboard_id = leaderboard['leaderboard_id']
            data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{leaderboard_id}')
            all_leaderboards_data.append(data)
        return True, all_leaderboards_data
    else:
        return False, {"message": "Leaderboard error"}


async def get_leaderboard_data_from_external_api(offset: int = 0, limit: int = 20, get_latest=False,
                                                 leaderboard_id: str = settings.leaderboard_id) -> Tuple[bool, dict]:
    q_param = {'offset': offset, "limit": limit}
    if get_latest:
        leaderboards_data = await fetch_data_from_external_api(q_param=q_param,
                                                               path=f'leaderboards/hubs/8a9629cf-c837-4389-97a1-1c47cf886df4')
        if leaderboards_data:
            leaderboard_id = max(leaderboards_data['items'], key=lambda x: x['start_date'])['leaderboard_id']
        else:
            return False, {"message": "Auth Error"}
    data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{leaderboard_id}')
    if data:
        new_items = []
        for item in data['items']:
            item_n = item.copy()
            item['player']['statistic'] = await collect_base_statistics(nickname=item_n['player']["nickname"],
                                                                        user_id=item_n['player']["user_id"])
            new_items.append(item)
        data['items'] = new_items
        return True, data
    else:
        return False, {"message": "Auth Error"}
