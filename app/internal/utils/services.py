from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.internal.models.user import *
from fastapi.security import OAuth2PasswordBearer

from jose import jwt, JWTError

from app.internal.utils.models import CommonHTTPException, TokenData
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
        user = user.first()
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


async def get_current_user(session : AsyncSession,token: str = Depends(oauth2_scheme), ):
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
    user = await get_user(session, nickname=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user
