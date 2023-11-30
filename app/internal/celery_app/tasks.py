import asyncio

from celery import shared_task

from app.internal.utils.services import prize_distribution


@shared_task()
def hello_world():
    print("Hello, world!")


@shared_task()
def award_on_1st_and_15th():
    result = prize_distribution()
    asyncio.run(result)
