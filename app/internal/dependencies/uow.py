from fastapi import Request
from sqlalchemy.orm import declarative_base

from app.internal.db.unit_of_work import SqlAlchemyUnitOfWork, CELERY_SESSION_FACTORY, ADMIN_SESSION_FACTORY


async def get_uow():
    uow = SqlAlchemyUnitOfWork()
    yield uow


def get_uow_for_celery():
    return SqlAlchemyUnitOfWork(session_factory=CELERY_SESSION_FACTORY)

def get_uow_for_admin():
    return SqlAlchemyUnitOfWork(session_factory=ADMIN_SESSION_FACTORY)
