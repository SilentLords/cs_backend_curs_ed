from datetime import datetime, timedelta
from typing import Annotated, List

import httpx
from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.internal.models.user import *
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from app.internal.utils.schemas import CommonHTTPException, TokenData, Statistic, BaseStatistic
from app.internal.utils.user import add_money_to_user
from app.pkg.postgresql import get_session, settings, async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_or_create_user(session: AsyncSession, nickname: str, openid: str):
    result = await session.execute(select(User).where(User.nickname == nickname))
    if res := result.scalars().all():
        return res
    new_user = User(nickname=nickname, openid=openid)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def get_user(nickname: str, session: AsyncSession):
    user = await session.execute(select(User).where(User.nickname == nickname))
    if user := user.unique().scalars().all():
        user = user[0]
        return user
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(session: AsyncSession, token: str = Depends(oauth2_scheme), ):
    credentials_exception = CommonHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(session=session, nickname=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


async def check_auth_user(token: str, session: AsyncSession):
    credentials_exception = CommonHTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(session=session, nickname=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def fetch_data_from_external_api(path: str, q_param: dict = None, ):
    headers = {'accept': 'application/json', 'Authorization': f'Bearer {settings.faceit_api_key}'}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://open.faceit.com/data/v4/{path}",
                                    params=q_param, headers=headers)

        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            return None


async def get_rating_place(nickname: str, player_id: str):
    data = await fetch_data_from_external_api(path=f'leaderboards/{settings.leaderboard_id}/players/{player_id}')
    if data:
        return data['position']
    return 0


async def get_matches_per_month(nickname: str, player_id: str):
    data = await fetch_data_from_external_api(q_param={'game': settings.game_id}, path=f'players/{player_id}/history')
    if data:
        return len(data['items'])
    return 0


async def get_matches_win_per_month(nickname: str, player_id: str):
    data = await fetch_data_from_external_api(q_param={'game': settings.game_id}, path=f'players/{player_id}/history')
    if data:
        win = 0
        for game in data['items']:
            winner = game['results']['winner']
            for team in game['teams'].keys():
                for player in game['teams'][team]['players']:
                    if player['player_id'] == player_id and winner == game['teams'][team]['nickname']:
                        win += 1
        return win
    return 0


async def get_life_time_stats(player_id: str, field_name: str, data: dict) -> float:
    # data = await fetch_data_from_external_api(path=f'players/{player_id}/stats/{settings.game_id}')
    if data:
        return len(data['lifetime'][field_name])
    return 0


async def get_k_r_percent(player_id: str, data) -> float:
    # data = await fetch_data_from_external_api(path=f'players/{player_id}/stats/{settings.game_id}')

    if data:
        sum_k_r = 0
        count = 0
        for segment in data['segments']:
            sum_k_r += float(segment['stats']['Average K/R Ratio'])
            count += 1
        return sum_k_r / count
    return 0


## НЕ ПОНЕЛ ГДЕ ИСКАТЬ
async def get_faceit_points(player_id: str, nickname: str):
    data = await fetch_data_from_external_api(path=f'players?nickname=evom_game', q_param={'nickname': nickname})
    if data:
        if 'cs2' in data['games'].keys():
            return data['games']['cs2']['faceit_elo']
    return 0


async def get_mounts_kills(player_id: str, data: dict) -> int:
    if data:
        sum_kills = 0
        count = 0
        for segment in data['segments']:
            sum_kills += int(segment['stats']['Kills'])
        return sum_kills
    return 0


async def collect_base_statistics(nickname: str, user_id: str) -> BaseStatistic:
    player_id = user_id
    data_for_stats = await fetch_data_from_external_api(path=f'players/{player_id}/stats/{settings.game_id}')
    k_d_avg_segments = await get_life_time_stats(player_id, 'K/D Ratio', data=data_for_stats)
    hs_percent = await get_life_time_stats(player_id, 'Total Headshots %', data=data_for_stats)
    kills = await get_mounts_kills(player_id, data=data_for_stats)
    return BaseStatistic(k_d_avg_segments=k_d_avg_segments, hs_percent=hs_percent, kills=kills)


async def collect_statistics(nickname: str, user_id: str) -> Statistic:
    player_id = user_id
    data_for_stats = await fetch_data_from_external_api(path=f'players/{player_id}/stats/{settings.game_id}')

    rating_place = await get_rating_place(nickname, player_id)
    matches_per_month = await get_matches_per_month(nickname, player_id)
    matches_win_per_month = await get_matches_win_per_month(nickname, player_id)
    matches_per_all_month = await get_life_time_stats(player_id, 'Matches', data=data_for_stats)
    win_rate = await get_life_time_stats(player_id, 'Win Rate %', data=data_for_stats)
    longest_win_streak = await get_life_time_stats(player_id, 'Longest Win Streak', data=data_for_stats)
    hs_percent = await get_life_time_stats(player_id, 'Total Headshots %', data=data_for_stats)
    k_r_avg_segments = await get_k_r_percent(player_id, data=data_for_stats)
    k_d_avg_segments = await get_life_time_stats(player_id, 'K/D Ratio', data=data_for_stats)
    # kills = await get_life_time_stats(player_id, 'Kills', data=data_for_stats)
    faceit_points = await get_faceit_points(player_id, nickname)

    stats = Statistic(nickname=nickname,
                      rating_rang=rating_place,
                      matches_win_per_month=matches_win_per_month,
                      matches_per_month=matches_per_month,
                      matches_per_all_month=matches_per_all_month,
                      win_rate=win_rate,
                      longest_win_streak=longest_win_streak,
                      hs_percent=hs_percent,
                      k_r_avg_segments=k_r_avg_segments,
                      k_d_avg_segments=k_d_avg_segments,
                      faceit_points=faceit_points,
                      )

    return stats


async def getting_list_best_players(offset: int, limit: int, get_latest: bool):
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


async def prize_distribution():
    """Функция начисляет призовые деньги"""
    offset = 0
    limit = 4
    get_latest = True
    awards = [100, 70, 50, 30]
    # получаем словарь турнирной таблицы
    try:
        leaderboard = await getting_list_best_players(offset, limit, get_latest)
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Ошибка получения лидерборда")
    top_players = leaderboard["items"]
    list_nic = []
    list_of_awarded_users = []

    # достаём никнеймы лидеров турнирной таблицы
    for gamer in top_players:
        nickname = gamer["player"]["nickname"]
        list_nic.append(nickname)

    for index, amount in enumerate(awards):
        # проверяем есть ли пользователь с таким ником в нашей БД
        async with async_session() as session:
            # try:
            user = await get_user(list_nic[index], session)
            # except Exception as ex:
            #     raise HTTPException(status_code=500, detail="Ошибка получения пользователя")
            print(list_nic[index])
            if not user:
                continue
            user_id = user.id
            transaction_type = "prize_money"
            amount = float(amount)
            try:
                awarded_user = await add_money_to_user(user_id, amount, transaction_type, session)
            except Exception as ex:
                raise HTTPException(status_code=500, detail="Ошибка начисления средств")
            list_of_awarded_users.append(awarded_user)
    return JSONResponse(content={'detail': f'Пользователи {list_nic} получили призовые'})
