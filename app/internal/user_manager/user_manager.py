from datetime import timedelta

from jose import jwt, JWTError
from starlette import status

from app.configuration.settings import settings
from app.internal.models import User
from app.internal.utils.schemas import CommonHTTPException, TokenData
from app.internal.utils.services import create_access_token


async def get_or_create_user(uow: 'SqlAlchemyUnitOfWork', nickname: str, guid: str) -> User:
    async with uow:
        user = await uow.user_actions.get_first_by_field("nickname", nickname)
        if user:
            return user
        new_user = User(nickname=nickname, openid=guid)
        uow.user_actions.add(new_user)
        await uow.session.commit()
        await uow.session.refresh(new_user)
        return new_user


async def check_auth_user(token: str, uow: 'SqlAlchemyUnitOfWork'):
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
    user = await get_user(field_name='nickname', field_value=token_data.username, uow=uow)
    if user is None:
        raise credentials_exception
    return user


async def change_web3_in_user(token: str, uow: 'SqlAlchemyUnitOfWork', ethereum_ID: str, ):
    user = await check_auth_user(token=token, uow=uow)
    async with uow:
        uow.user_actions.update(user, {'ethereum_ID': ethereum_ID})
        uow.commit()


async def get_user(field_name: str, field_value: str | int, uow: 'SqlAlchemyUnitOfWork') -> User | None:
    async with uow:
        user = await uow.user_actions.get_first_by_field(field_name, field_value)
    return user


async def auth_user(client, request, uow):
    token = await client.authorize_access_token(request)
    user = await client.userinfo(token=token)
    request.session["user"] = dict(user)
    _ = await get_or_create_user(uow, request.session['user']['nickname'], request.session['user']['guid'])
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": request.session['user']['nickname']}, expires_delta=access_token_expires
    )
    redirect_uri = '/'
    return access_token, redirect_uri


