from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from datetime import datetime, timedelta

from app.configuration.settings import settings
from app.internal.models import User, Token
# from app.internal.routes.users import oauth2_scheme
from app.internal.utils.services import create_access_token
from app.pkg.postgresql import get_session


ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(
    prefix='/api/v1/auth/users'
)

# Создаем OAuth2PasswordBearer объект для авторизации
auth = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/users/login/token")
# Создаем хешер для паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Функция для проверки пароля"""
    return pwd_context.verify(plain_password, hashed_password)


# Роут для регистрации нового пользователя
@router.post("/register")
async def register_user(db: AsyncSession = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    # Проверка, что пользователь с таким nickname не существует
    result = await db.execute(select(User).filter(User.nickname == form_data.username))
    existing_user = result.scalar()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this nickname already exists",
        )

    # Хеширование пароля
    hashed_password = pwd_context.hash(form_data.password)

    # Создание нового пользователя
    new_user = User()
    new_user.nickname = form_data.username
    new_user.password = hashed_password
    db.add(new_user)
    await db.commit()

    return {"message": "User successfully registered"}


# Роут для создания токена
@router.post("/login/token")
async def login_for_access_token(db: AsyncSession = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    query = await db.execute(select(User).filter(User.nickname == form_data.username))
    user = query.scalar()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.nickname}, expires_delta=access_token_expires
    )

    # Сохраняем токен в базе данных
    db_token = Token(access_token=access_token, token_type="bearer")
    db.add(db_token)
    await db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


# Роут для выхода пользователя
@router.post("/logout")
async def logout_user(token: str = Depends(auth), db: AsyncSession = Depends(get_session)):
    # Декодируем токен, чтобы получить информацию о пользователе
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Здесь вы можете реализовать логику для удаления токена из базы данных
    # Например, если у вас есть таблица Token в базе данных
    query_result = await db.execute(select(Token).filter(Token.access_token == token))
    db_token = query_result.scalar()
    if db_token:
        await db.delete(db_token)
        await db.commit()

    return {"message": "User successfully logged out"}


# Роут для защищенного контента
@router.get("/protected")
async def protected_route(token: str = Depends(auth)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return {"message": "You are authenticated"}
