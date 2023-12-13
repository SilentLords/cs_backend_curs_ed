from app.internal.models import BillingAccount
from app.internal.repository.base import SqlAlchemyRepositoryBase


class BillingAccountSqlAlchemyRepository(SqlAlchemyRepositoryBase):

    def __init__(self, session) -> None:
        super().__init__(session, BillingAccount)