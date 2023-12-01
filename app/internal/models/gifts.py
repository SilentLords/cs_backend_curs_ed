from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, MetaData, Table, DateTime, func, Date
from app.internal.utils.enums import GIFT_EVENT_STATUS_CHOICES_ENUM
from .base import Base, ChoiceType
from sqlalchemy.dialects.postgresql import ENUM as PgEnum


class GiftEvent(Base):
    # Todo: create alembic migration and insert in_progress events for December 1 and December 8
    # https://stackoverflow.com/questions/24612395/how-do-i-execute-inserts-and-updates-in-an-alembic-upgrade-script
    __tablename__ = 'gift_events'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(PgEnum(GIFT_EVENT_STATUS_CHOICES_ENUM, name='gift_status', create_type=False), nullable=False,
                    default=GIFT_EVENT_STATUS_CHOICES_ENUM.IN_PROGRESS)
    start_at = Column(Date, server_default=func.now(), nullable=False)
    top_one_count = Column(Integer, default=0)
    top_two_count = Column(Integer, default=0)
    top_three_count = Column(Integer, default=0)
    top_four_count = Column(Integer, default=0)
    leaderboard_id = Column(String, nullable=False)

    def __repr__(self):
        return f"<GiftEvent(id={self.id}, status={self.status}, start_at={self.start_at})>"
