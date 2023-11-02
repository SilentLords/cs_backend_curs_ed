import asyncio

import typer as typer
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.sessions import SessionMiddleware

from app.configuration.server import Server
from app.configuration.settings import settings
from app.internal.models import __models__
from app.pkg.postgresql import init_models

app_: FastAPI
cli = typer.Typer()


def create_app(_=None) -> FastAPI:
    global app_
    app = FastAPI()
    app_ = Server(app).get_class()
    app_.add_middleware(SessionMiddleware, secret_key="your-secret-key")

    return Server(app).get_class()


app_ = create_app()


@cli.command()
def db_init_models():
    asyncio.run(init_models())
    print("Done")

cli()
# @app_.get("/docs")
# def read_docs():
#     return get_swagger_ui_html(openapi_url="/openapi.json")
#
# @app_.on_event("startup")
# async def startup_event():
#     client = AsyncIOMotorClient(settings.db_url)
#     print(client, settings.db_url, settings.db_name)
#     await init_beanie(
#         database=client[settings.db_name], document_models=__models__
#     )
