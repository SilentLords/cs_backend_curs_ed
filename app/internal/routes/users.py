from datetime import timedelta
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from authlib.integrations.starlette_client import OAuthError
from app.internal.models.user import User
from app.configuration.settings import settings
from app.internal.utils.oauth import register_oauth
from app.internal.utils.services import get_or_create_user, create_access_token, get_current_active_user, \
    get_current_user
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
async def login(request: Request):
    redirect_uri = settings.oauth_authorize_redirect_path
    print(redirect_uri)
    return await oauth.create_client("Client_cs2").authorize_redirect(request, redirect_uri, redirect_popup=True)


@router.get("/me")
async def get_me( session: AsyncSession = Depends(get_session)):
    current_user = await get_current_user(session)
    return current_user

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
        return RedirectResponse(url=f"/?token={access_token}")
    except OAuthError as e:
        return JSONResponse({"error": "OAuth error", "message": str(e)})


@router.delete("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
