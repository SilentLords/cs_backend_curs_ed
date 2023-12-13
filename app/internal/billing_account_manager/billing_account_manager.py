from typing import Tuple

from app.internal.models import BillingAccount, User
from app.internal.user_manager.user_manager import get_user
from app.internal.utils.schemas import T


async def get_or_create_billing_account(uow: 'SqlAlchemyUnitOfWork', user: User):
    async with uow:
        billing_account = await uow.billing_account_actions.get_first_by_field('user_id', user.id)

        if not billing_account:
            billing_account = BillingAccount(user_id=user.id, user=user)
            uow.billing_account_actions.add(billing_account)
            await uow.session.commit()
            await uow.session.refresh(billing_account)

    return billing_account
