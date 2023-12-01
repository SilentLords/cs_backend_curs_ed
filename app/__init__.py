import asyncio

import typer as typer
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware

from app.configuration.server import Server
from app.configuration.settings import settings
from app.internal.models import __models__, GiftEvent
from app.pkg.postgresql import  engine, get_session
from starlette_admin.contrib.sqla import Admin, ModelView
from app.internal.models import __models__
from app.admin_views import GiftEventModelView, UsernameAndPasswordProvider

app_: FastAPI


def create_app(_=None) -> FastAPI:
    global app_

    app = FastAPI(middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])])
    app_ = Server(app).get_class()
    app_.add_middleware(SessionMiddleware, secret_key="your-secret-key")
    return Server(app).get_class()


app_ = create_app()
admin = Admin(engine,
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(SessionMiddleware, secret_key="your-secret-key")],
              )
__models__.remove(GiftEvent)
admin.add_view(GiftEventModelView(GiftEvent))
for model in __models__:
    admin.add_view(ModelView(model))
admin.mount_to(app_)
