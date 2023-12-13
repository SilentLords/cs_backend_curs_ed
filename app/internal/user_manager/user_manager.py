from app.internal.models import User
from app.internal.utils.schemas import CommonHTTPException, TokenData
from starlette import status
from app.configuration.settings import settings
from jose import jwt, JWTError


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
    user = await get_user(nickname=token_data.username, uow=uow)
    if user is None:
        raise credentials_exception
    return user


async def get_user(nickname: str, uow: 'SqlAlchemyUnitOfWork') -> User | None:
    async with uow:
        user = await uow.user_actions.get_first_by_field("nickname", nickname)
    return user
