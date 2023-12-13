import httpx
from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.utils.schemas import CommonResponse, Content
from app.internal.utils.services import fetch_data_from_external_api, settings, collect_statistics, \
    collect_base_statistics
from app.pkg.postgresql import get_session

router = APIRouter(
    prefix='/backend/api/v1/leaderboard'
)


@router.get('/')
async def get_leaderboard(offset: int, limit: int = 20, get_latest: bool = False):
    leaderboard_id: str = settings.leaderboard_id
    q_param = {'offset': offset, "limit": limit}
    if get_latest:
        leaderboards_data = await fetch_data_from_external_api(q_param=q_param,
                                                               path=f'leaderboards/hubs/8a9629cf-c837-4389-97a1-1c47cf886df4')
        if leaderboards_data:
            leaderboard_id = max(leaderboards_data['items'], key=lambda x: x['start_date'])['leaderboard_id']
        else:
            return {"message": "Auth Error"}

    data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{leaderboard_id}')
    if data:
        new_items = []
        for item in data['items']:
            item_n = item.copy()
            item['player']['statistic'] = await collect_base_statistics(nickname=item_n['player']["nickname"],
                                                                        user_id=item_n['player']["user_id"])
            new_items.append(item)
        data['items'] = new_items
        return data
    else:
        return {"message": "Auth Error"}

@router.get("/get_leaderboard/{leaderboard_id}")
async def get_all_leaderboards(leaderboard_id:str, offset: int, limit: int = 20):
    q_param = {'offset': offset, "limit": limit}
    data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{leaderboard_id}')

    if data:
        new_items = []
        for item in data['items']:
            item_n = item.copy()
            item['player']['statistic'] = await collect_base_statistics(nickname=item_n['player']["nickname"],
                                                                        user_id=item_n['player']["user_id"])
            new_items.append(item)
        data['items'] = new_items
        return data
    else:
        return {"message": data}




@router.get("/get_all_leaderboards")
async def get_all_leaderboards(offset: int, limit: int = 20):
    q_param = {'offset': offset, "limit": limit}
    leaderboards_data = await fetch_data_from_external_api(q_param=q_param,
                                                           path=f'leaderboards/hubs/8a9629cf-c837-4389-97a1-1c47cf886df4')

    if leaderboards_data:

        all_leaderboards_data = []
        for leaderboard in leaderboards_data['items']:
            leaderboard_id = leaderboard['leaderboard_id']
            data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{leaderboard_id}')
            all_leaderboards_data.append(data)
        return all_leaderboards_data
    else:
        return {"message": "Leaderboard error"}
@router.get("/get_lastest_leaderboard")
async def get_lastest_leaderboard(offset: int, limit: int = 20):
    q_param = {'offset': offset, "limit": limit}
    leaderboards_data = await fetch_data_from_external_api(q_param=q_param,
                                                           path=f'leaderboards/hubs/8a9629cf-c837-4389-97a1-1c47cf886df4')
    if leaderboards_data:
        latest_leaderboard_id = max(leaderboards_data['items'], key=lambda x: x['start_date'])['leaderboard_id']
        data = await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{latest_leaderboard_id}')
        new_items = []
        for item in data['items']:
            item_n = item.copy()
            item['player']['statistic'] = await collect_base_statistics(nickname=item_n['player']["nickname"],
                                                                        user_id=item_n['player']["user_id"])
            new_items.append(item)
        data['items'] = new_items
        return data
    else:
        return {"message": "Auth Error"}

# @router.get('/test_new_func')test_new_func
# async def test_new_func():
#     return await prize_distribution()
