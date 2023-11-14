import httpx
from fastapi import APIRouter

from app.internal.utils.schemas import CommonResponse, Content
from app.internal.utils.services import fetch_data_from_external_api, settings, collect_statistics, collect_base_statistics

router = APIRouter(
    prefix='/backend/api/v1/leaderboard'
)


@router.get('/')
async def get_leaderboard(offset: int, limit: int = 20):
    q_param = {'offset': offset, "limit": limit}
    data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{settings.leaderboard_id}')
    new_items = []
    for item in data['items']:
        item_n = item.copy()
        item['player']['statistic'] = await collect_base_statistics(nickname=item_n['player']["nickname"],
                                                               user_id=item_n['player']["user_id"])
        new_items.append(item)
    data['items'] = new_items
    return data
