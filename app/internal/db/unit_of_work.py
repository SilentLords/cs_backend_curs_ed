import abc

import ssl

from collections import deque

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.configuration.settings import settings
from app.internal.repository.gift_event import GiftEventSqlAlchemyRepository

ca_path = "app/certs/ca-certificate.crt"
my_ssl_context = ssl.create_default_context(cafile=ca_path)
my_ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context = {"ssl": my_ssl_context} if settings.is_prod == "true" else {}

SQLALCHEMY_DATABASE_URL = (
    f'postgresql+asyncpg://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
)

celery_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, poolclass=NullPool, connect_args=ssl_context)
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, connect_args=ssl_context)

DEFAULT_SESSION_FACTORY = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
CELERY_SESSION_FACTORY = sessionmaker(celery_engine, expire_on_commit=False, class_=AsyncSession)


class AbstractUnitOfWork(abc.ABC):
    def __init__(self) -> None:
        self.events = deque()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError

    def add_event(self, event):
        self.events.append(event)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        super().__init__()
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        self.gift_event_actions = GiftEventSqlAlchemyRepository(session=self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        self.session.expunge_all()
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
