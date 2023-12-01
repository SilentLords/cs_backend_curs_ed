from sqlalchemy import Column, Integer, DateTime, func, Date
from app.internal.utils.enums import GIFT_EVENT_STATUS_CHOICES
from .base import Base, ChoiceType


class GiftEvent(Base):
    # Todo: create alembic migration and insert in_progress events for December 1 and December 8
    # https://stackoverflow.com/questions/24612395/how-do-i-execute-inserts-and-updates-in-an-alembic-upgrade-script
    __tablename__ = 'gift_events'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(ChoiceType(GIFT_EVENT_STATUS_CHOICES))
    start_at = Column(Date, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<GiftEvent(id={self.id}, status={self.status}, start_at={self.start_at})>"
