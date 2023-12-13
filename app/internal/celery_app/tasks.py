import asyncio

from celery import shared_task

from app.configuration.settings import Settings
from app.internal.dependencies.uow import get_uow_for_celery
from app.internal.gift_event_manager.gift_event_manager import start_distribute_gifts

settings = Settings()


@shared_task()
def hello_world():
    print("Hello, world!")


async def create_session(a_session):
    async with a_session() as session:
        return session


@shared_task()
def distribute_gifts():
    uow = get_uow_for_celery()
    asyncio.run(start_distribute_gifts(uow))
