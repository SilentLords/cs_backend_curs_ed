from datetime import datetime, timedelta
from typing import Annotated

import httpx
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.internal.models.user import *
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from app.internal.utils.schemas import CommonHTTPException, TokenData, Statistic
from app.pkg.postgresql import get_session, settings

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
    if user := user.scalars().all():
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
        response = await client.get("https://open.faceit.com/data/v4/",
                                    params=q_param, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return None


async def get_rating_place(nickname: str, player_id: str):
    data = await fetch_data_from_external_api(path=f'leaderboards/{settings.leaderboard_id}/players/{player_id}')
    return data['position']


async def collect_statistics(nickname: str, user_id: str) -> Statistic:
    player_id = user_id
    rating_place = await get_rating_place(nickname, player_id)
    stats = Statistic(rating_rang=rating_place)
    return stats
