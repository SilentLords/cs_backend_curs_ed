from authlib.integrations.starlette_client import OAuthError
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse

from app.configuration.settings import settings
from app.internal.dependencies.uow import get_uow
from app.internal.user_manager.user_manager import check_auth_user, change_web3_in_user, auth_user
from app.internal.utils import schemas
from app.internal.utils.oauth import register_oauth
from app.internal.utils.schemas import Statistic
from app.internal.utils.services import collect_statistics
from app.internal.utils.services import fetch_data_from_external_api

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter(
    prefix='/backend/api/v1/users'
)

oauth = register_oauth()


@router.get('/hub')
async def get_hub_count(request: Request) -> schemas.UsersHub:
    data = await fetch_data_from_external_api(path=f'hubs/8a9629cf-c837-4389-97a1-1c47cf886df4')
    r_data = schemas.UsersHub(count=data['players_joined'])
    return r_data


@router.get("/login")
async def login(request: Request, redirect_uri: str):
    redirect_callback_uri = settings.oauth_authorize_redirect_path
    request.session["redirect_uri"] = redirect_uri
    return await oauth.create_client("Client_cs2").authorize_redirect(request, redirect_callback_uri,
                                                                      redirect_popup=True)


@router.get("/me", response_model=schemas.User)
async def get_me(uow: 'SqlAlchemyUnitOfWork' = Depends(get_uow), token: str = Depends(oauth2_scheme), ) -> schemas.User:
    user = await check_auth_user(token=token, uow=uow)
    user.statistic = await collect_statistics(nickname=user.nickname, user_id=user.openid)
    # print(user)
    return user


@router.get("/check_my_web3")
async def check_my_web3(uow=Depends(get_uow),
                        token: str = Depends(oauth2_scheme)):
    user = await check_auth_user(token=token, uow=uow)
    if user.ethereum_ID:
        return {"has_web3": True}
    # print(user)
    return {"has_web3": False}


@router.put("/me/change_ethereum_id")
async def change_ethereum_id(ethereum_ID: str, uow: 'SqlAlchemyUnitOfWork' = Depends(get_uow),
                             token: str = Depends(oauth2_scheme), ):
    await change_web3_in_user(token=token, uow=uow, ethereum_ID=ethereum_ID)
    return {}


@router.get('/statistic')
async def get_statistic(uow: 'SqlAlchemyUnitOfWork' = Depends(get_uow),
                        token: str = Depends(oauth2_scheme), ) -> Statistic:
    user = await check_auth_user(token=token, uow=uow)
    statistic = await collect_statistics(nickname=user.nickname, user_id=user.openid)
    return statistic


@router.get("/login/callback")
async def auth(request: Request, uow: "SqlAlchemyUnitOfWork" = Depends(get_uow)):
    client = oauth.create_client("Client_cs2")
    try:
        access_token, redirect_uri = await auth_user(client, request, uow)
        if request.session.get('redirect_uri'):
            redirect_uri = request.session.get('redirect_uri')
        return RedirectResponse(url=f"{redirect_uri}?token={access_token}")
    except OAuthError as e:
        return JSONResponse({"error": "OAuth error", "message": str(e)})


@router.delete("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
