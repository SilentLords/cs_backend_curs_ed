import httpx
from fastapi import APIRouter

from app.internal.utils.schemas import CommonResponse, Content
from app.internal.utils.services import fetch_data_from_external_api, settings

router = APIRouter(
    prefix='/api/v1/leaderboard'
)


@router.get('/')
async def get_leaderboard(offset: int, limit: int = 20):
    q_param = {'offset': offset, "limit": limit}
    return await fetch_data_from_external_api(q_param=q_param, path=f'leaderboards/{settings.leaderboard_id}')
