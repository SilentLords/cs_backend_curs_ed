from app.internal.models import WithdrawRequest
from app.internal.repository.base import SqlAlchemyRepositoryBase


class WithdrawRequestSqlAlchemyRepository(SqlAlchemyRepositoryBase):
    def __init__(self, session) -> None:
        super().__init__(session, WithdrawRequest)