from app.internal.models import Transaction
from app.internal.repository.base import SqlAlchemyRepositoryBase


class TransactionSqlAlchemyRepository(SqlAlchemyRepositoryBase):
    def __init__(self, session) -> None:
        super().__init__(session, Transaction)
