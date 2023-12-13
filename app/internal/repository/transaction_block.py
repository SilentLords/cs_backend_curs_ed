from app.internal.models import TransactionBlock
from app.internal.repository.base import SqlAlchemyRepositoryBase


class TransactionBlockSqlAlchemyRepository(SqlAlchemyRepositoryBase):
    def __init__(self, session) -> None:
        super().__init__(session, TransactionBlock)