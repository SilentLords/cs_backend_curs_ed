from app.internal.models import GiftEvent
from app.internal.routes.leaderboards import get_lastest_leaderboard


async def create_new_gift_event(uow: 'SqlAlchemyUnitOfWork'):
    async with uow:
        leaderboard = await get_lastest_leaderboard(offset=1, limit=1)

        leaderboard_data = leaderboard.get('leaderboard')

        if leaderboard_data:
            gift_event = GiftEvent(season_name=leaderboard_data.get('leaderboard_name'),
                                   leaderboard_id=leaderboard_data.get('leaderboard_id'))
            uow.gift_event_actions.add(gift_event)
            await uow.session.commit()
