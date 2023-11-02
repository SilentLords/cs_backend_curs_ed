from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from authlib.common.security import generate_token
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from authlib.integrations.starlette_client import OAuthError

from app.configuration.settings import settings
from app.internal.utils.oauth import register_oauth

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
    redirect_uri = 'https://cs2-backend.evom.dev/api/v1/users/login/callback'
    nonce = generate_token()
    print(redirect_uri)
    return await oauth.create_client("Client_cs2").authorize_redirect(request, redirect_uri, redirect_popup=True, nonce=nonce)


@router.get("/login/callback")
async def auth(request: Request):
    print('req:', request.query_params)
    new_req = request
    try:
        token = await oauth.create_client("Client_cs2").authorize_access_token(request)
        # print(token)
        # user = await oauth.create_client("Client_cs2").parse_id_token(token=token)
        request.session["user"] = token['userinfo']
        print(request.session["user"])
        return RedirectResponse(url="/")
    except OAuthError as e:
        return JSONResponse({"error": "OAuth error", "message": str(e)})


@router.delete("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
