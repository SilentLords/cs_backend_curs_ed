from app.internal.transaction_manager.transaction_manager import prize_distribution
from app.internal.utils.enums import GIFT_EVENT_STATUS_CHOICES_ENUM
import datetime

from app.internal.models import GiftEvent
from app.internal.routes.leaderboards import get_latest_leaderboard



async def create_new_gift_event(uow: 'SqlAlchemyUnitOfWork'):
    async with uow:
        leaderboard = await get_latest_leaderboard(offset=0, limit=1)

        leaderboard_data = leaderboard.get('leaderboard')

        if leaderboard_data:
            gift_event = GiftEvent(season_name=leaderboard_data.get('leaderboard_name'),
                                   leaderboard_id=leaderboard_data.get('leaderboard_id'))
            uow.gift_event_actions.add(gift_event)
            await uow.session.commit()

#['jaw1ko', 'larik-_-', 'Clash_RideR', 'Alamov']
async def start_distribute_gifts(uow: 'SqlAlchemyUnitOfWork'):
    async with uow:
        gift = await uow.gift_event_actions.get_first_by_field('start_at', datetime.date.today())
        print(gift, gift.is_approved, gift.status)
        if gift:
            if gift.is_approved and gift.status == GIFT_EVENT_STATUS_CHOICES_ENUM.IN_PROGRESS:
                result = await prize_distribution(gift)
