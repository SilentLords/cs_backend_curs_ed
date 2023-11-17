from datetime import timedelta
from typing import Annotated

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from authlib.integrations.starlette_client import OAuthError
from app.internal.models.user import User
from app.configuration.settings import settings
from app.internal.utils import schemas
from app.internal.utils.schemas import CommonHTTPException, TokenData, Statistic
from app.internal.utils.oauth import register_oauth
from app.internal.utils.services import get_or_create_user, create_access_token, get_current_active_user, \
    get_current_user, get_user, check_auth_user, collect_statistics
from app.internal.utils.user import add_money_to_user, debit_user_money, freeze_user_money, unfreeze_user_money
from app.pkg.postgresql import get_session
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix='/api/v1/users'
)

oauth = register_oauth()


@router.get("/")
async def home(request: Request):
    # Проверяем, авторизован ли пользователь
    if not request.session.get("user"):
        return {"message": "Добро пожаловать! Войдите с помощью OAuth."}
    return {"message": f"Привет, {request.session['user']}!"}


@router.get("/login")
async def login(request: Request, redirect_uri: str):
    redirect_callback_uri = settings.oauth_authorize_redirect_path
    request.session["redirect_uri"] = redirect_uri
    print(redirect_callback_uri)
    return await oauth.create_client("Client_cs2").authorize_redirect(request, redirect_callback_uri,
                                                                      redirect_popup=True)


@router.get("/me", response_model=schemas.User)
async def get_me(session: AsyncSession = Depends(get_session), token: str = Depends(oauth2_scheme), ) -> schemas.User:
    user = await check_auth_user(token=token, session=session)
    user.statistic = await collect_statistics(nickname=user.nickname, user_id=user.openid)
    # print(user)
    return user


@router.get('/statistic')
async def get_statistic(session: AsyncSession = Depends(get_session),
                        token: str = Depends(oauth2_scheme), ) -> Statistic:
    user = await check_auth_user(token=token, session=session)
    print("Nickname:", user.nickname)
    statistic = await collect_statistics(nickname=user.nickname, user_id=user.openid)
    return statistic


@router.get("/login/callback")
async def auth(request: Request, session: AsyncSession = Depends(get_session)):
    client = oauth.create_client("Client_cs2")
    try:
        token = await client.authorize_access_token(request)
        user = await client.userinfo(token=token)
        request.session["user"] = dict(user)
        res = await get_or_create_user(session, request.session['user']['nickname'], request.session['user']['guid'])
        print(res)
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": request.session['user']['nickname']}, expires_delta=access_token_expires
        )
        redirect_uri = '/'
        if request.session.get('redirect_uri'):
            redirect_uri = request.session.get('redirect_uri')
        return RedirectResponse(url=f"{redirect_uri}?token={access_token}")
    except OAuthError as e:
        return JSONResponse({"error": "OAuth error", "message": str(e)})


@router.delete("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@router.post("/add_money/{user_id}")
async def add_money(user_id: int, amount: float, transaction_type: str, db: AsyncSession = Depends(get_session)):
    """Добавление денег пользователю"""
    return await add_money_to_user(user_id, amount, transaction_type, db)


@router.post("/debit_money/{user_id}")
async def debit_money(user_id: int, amount: float, transaction_type: str, db: AsyncSession = Depends(get_session)):
    """Списание средств с баланса пользователя"""
    return await debit_user_money(user_id, amount, transaction_type, db)


@router.post("/freeze_money/{transaction_id}")
async def freeze_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Заморозка средств пользователя"""
    return await freeze_user_money(transaction_id, db)


@router.post("/unfreeze_money/{transaction_id}")
async def unfreeze_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Разморозка средств пользователя"""
    return await unfreeze_user_money(transaction_id, db)
