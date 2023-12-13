from app.internal.models import User
from app.internal.repository.base import SqlAlchemyRepositoryBase


class UserSqlAlchemyRepository(SqlAlchemyRepositoryBase):

    def __init__(self, session) -> None:
        super().__init__(session, User)
