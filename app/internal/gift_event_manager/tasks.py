import asyncio

from celery import shared_task

from app.internal.dependencies.uow import get_uow_for_celery
from app.internal.gift_event_manager.gift_event_manager import create_new_gift_event


@shared_task()
def create_new_gift_event_task():
    uow = get_uow_for_celery()

    asyncio.run(create_new_gift_event(uow=uow))
