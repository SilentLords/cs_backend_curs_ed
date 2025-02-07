from typing import Any

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin import EnumField, row_action, DateTimeField
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError, LoginFailed

from app.internal.db.unit_of_work import SqlAlchemyUnitOfWork
from app.internal.dependencies.uow import get_uow_for_admin
from app.internal.gift_event_manager.gift_event_manager import create_new_gift_event
from app.internal.user_manager.user_manager import get_user
from app.internal.utils.auth import pwd_context
from app.internal.utils.enums import GIFT_EVENT_STATUS_CHOICES_ENUM


def verify_password(plain_password, hashed_password):
    """Функция для проверки пароля"""
    return pwd_context.verify(plain_password, hashed_password)


async def find_user(nickname: str, uow: 'SqlAlchemyUnitOfWork') -> bool:
    user = await get_user("nickname", nickname, uow=uow)
    if user:
        return True
    else:
        return False


async def auth_user(nickname: str, password: str) -> bool:
    uow = get_uow_for_admin()
    user = await get_user("nickname", nickname, uow=uow)
    print(user, verify_password(password, user.password), user.is_admin)
    if not user or not verify_password(password, user.password) or not user.is_admin:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True


class GiftEventModelView(ModelView):
    fields = [
        EnumField("status", enum=GIFT_EVENT_STATUS_CHOICES_ENUM, exclude_from_edit=True, read_only=True, disabled=True),
        "season_name",
        "is_approved",
        DateTimeField("start_at", help_text="Все данные указываются в часовом поясе UTC (+0) "),
        "top_one_count",
        "top_two_count",
        "top_three_count",
        "top_four_count",
        "leaderboard_id", ]

    row_actions = ["view", "edit", "create_gift_event", "delete"]

    @row_action(
        name="create_gift_event",
        text="Создать новый GiftEvent",
        confirmation="Вы уверены что хотите создать новый GiftEvent?",
        icon_class="fas fa-check-circle",
        submit_btn_text="Подтвердить",
        submit_btn_class="btn-success",
        action_btn_class="btn-info",
    )
    async def create_new_gift_event_button(self, request: Request, pk: Any) -> str:
        uow = SqlAlchemyUnitOfWork()
        await create_new_gift_event(uow=uow)
        return 'GiftEvent успешно создан'


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
            """Save `username` in session"""
            request.session["username"] = username
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        if 'username' in request.session.keys():
            uow = get_uow_for_admin()
            if await find_user(request.session["username"], uow):
                user = await get_user('nickname', request.session["username"], uow=uow)
                request.state.user = user
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
