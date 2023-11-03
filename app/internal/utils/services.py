from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.internal.models.user import *


async def get_or_create_user(session: AsyncSession, nickname: str, ):
    result = await session.execute(select(users).where(users.nickname == nickname))
    if res := result.scalars().all():
        return res
    new_user = users(nickname=nickname)
    session.add(new_user)
    return new_user
