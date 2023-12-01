from urllib.parse import urljoin
import httpx
import requests

from app.configuration.settings import settings

async def fetch_data_from_external_api_basic(path: str, q_param: dict = None, ):
    async with httpx.AsyncClient() as client:
        response = await client.get(path,
                                    params=q_param,)

        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            return None


async def get_ABI(contract_address):
    url = urljoin(settings.bscscan_base_url, "api")
    params={
        "apikey": settings.bscscan_api_key,
        "module": "contract",
        "action": "getabi",
        "address": contract_address
    }
    abi = await fetch_data_from_external_api_basic(path=url,q_param=params)
    return abi['result']


async def get_transactions(address, start_block=0):
    url = urljoin(settings.bscscan_base_url, "api")
    params={
        "apikey": settings.bscscan_api_key,
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": start_block,
        "sort": "asc"
    }
    abi = await fetch_data_from_external_api_basic(path=url,q_param=params)
    return abi['result']