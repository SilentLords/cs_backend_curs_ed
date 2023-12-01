import asyncio

from fastapi import HTTPException
from select import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette_admin import EnumField
from starlette_admin.contrib.sqla import Admin, ModelView

from app.internal.models import User
from app.internal.utils.auth import pwd_context
from app.internal.utils.enums import GIFT_EVENT_STATUS_CHOICES_ENUM
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from app.internal.utils.services import get_user
from app.pkg.postgresql import async_session


async def get_session():
    async with async_session() as session:
        return session


def verify_password(plain_password, hashed_password):
    """Функция для проверки пароля"""
    return pwd_context.verify(plain_password, hashed_password)


async def auth_user(nickname: str, password: str) -> bool:
    session = await get_session()

    user = await get_user(nickname=nickname, session=session)
    print(user, verify_password(password, user.password), user.is_admin)
    if not user or not verify_password(password, user.password) or not user.is_admin:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


class GiftEventModelView(ModelView):
    fields = [EnumField("status", enum=GIFT_EVENT_STATUS_CHOICES_ENUM, read_only=True, disabled=True),
              "start_at",
              "top_one_count",
              "top_two_count",
              "top_three_count",
              "top_four_count",
              "leaderboard_id", ]


users = {
    "admin": {
        "name": "Admin",
        "avatar": "admin.png",
        "company_logo_url": "admin.png",
        "roles": ["read", "create", "edit", "delete", "action_make_published"],
    },
}


class UsernameAndPasswordProvider(AuthProvider):
    """
    This is only for demo purpose, it's not a better
    way to save and validate user credentials
    """

    async def login(
            self,
            username: str,
            password: str,
            remember_me: bool,
            request: Request,
            response: Response,
    ) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )

        if await auth_user(username, password):
            print('sosi hui')
            """Save `username` in session"""
            request.session["username"] = username
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        if request.session.get("username", None) in users:
            """
            Save current `user` object in the request state. Can be used later
            to restrict access to connected user.
            """
            request.state.user = users.get(request.session["username"])
            return True

        return False

    # def get_admin_config(self, returnequest: Request) -> AdminConfig:
    #     user = request.state.user  # Retrieve current user
    #     # Update app title according to current_user
    #     custom_app_title = "Hello, " + user["name"] + "!"
    #     # Update logo url according to current_user
    #     custom_logo_url = None
    #     if user.get("company_logo_url", None):
    #         custom_logo_url = request.url_for("static", path=user["company_logo_url"])
    #     return AdminConfig(
    #         app_title=custom_app_title,
    #         logo_url=custom_logo_url,
    #     )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        # photo_url = None
        # if user["avatar"] is not None:
        #     photo_url = request.url_for("static", path=user["avatar"])
        return AdminUser(username='admin', photo_url='')

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
