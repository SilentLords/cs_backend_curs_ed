from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.models.user import *


async def get_or_create_user(session: AsyncSession, nickname: str, ):
    result = await session.execute(select(User).where(User.nickname == nickname))
    if res := result.scalars().all():
        return res
    new_user = User(nickname=nickname)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
