from app.internal.models import GiftEvent
from app.internal.repository.base import SqlAlchemyRepositoryBase


class GiftEventSqlAlchemyRepository(SqlAlchemyRepositoryBase):
    def __init__(self, session) -> None:
        super().__init__(session, GiftEvent)
