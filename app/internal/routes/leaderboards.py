import httpx
from fastapi import APIRouter

router = APIRouter(
    prefix='/api/v1/leaderboard'
)


async def fetch_data_from_external_api(q_param: dict, headers: dict):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://open.faceit.com/data/v4/leaderboards/651da31af3e96d2044a35366", params=q_param, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None


@router.get('/')
async def get_leaderboard(offset: int, limit: int = 20):
    api_key = "2a4e3640-5b2f-41a8-9be4-756476cfa0d6"
    q_param = {'offset': offset, "limit": limit}
    headers = {'accept': 'application/json', 'Authorization': f'Bearer {api_key}'}
