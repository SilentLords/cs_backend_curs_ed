from fastapi import APIRouter

from app.internal.leaderboards_manager.leaderboard_manager import (
    get_leaderboard_data_from_external_api,
    get_all_leaderboard_data_from_external_api)

router = APIRouter(
    prefix='/backend/api/v1/leaderboard'
)


@router.get('/')
async def get_leaderboard(offset: int, limit: int = 20, get_latest: bool = False):
    status, data = await get_leaderboard_data_from_external_api(offset, limit, get_latest)
    return data


@router.get("/get_leaderboard/{leaderboard_id}")
async def get_all_leaderboards(leaderboard_id: str, offset: int, limit: int = 20):
    status, data = await get_leaderboard_data_from_external_api(offset, limit, leaderboard_id=leaderboard_id)
    return data


@router.get("/get_all_leaderboards")
async def get_all_leaderboards(offset: int = 0, limit: int = 20):
    status, data = await get_all_leaderboard_data_from_external_api(offset, limit)
    return data


@router.get("/get_latest_leaderboard")
async def get_latest_leaderboard(offset: int = 0, limit: int = 20):
    status, data = await get_leaderboard_data_from_external_api(offset, limit, get_latest=True)
    return data
