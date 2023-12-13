import decimal
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter

from app.internal.dependencies.uow import get_uow
from app.internal.transaction_block_manager.transaction_block_manager import freeze_user_money
from app.internal.utils.enums import WITHDRAW_REQUEST_STATUS_CHOICES_ENUM
from app.internal.models import WithdrawRequest, BillingAccount
from app.internal.utils.contract import withdraw_money_to_address
from app.internal.utils.blockchain_utils import convert_decimal_to_evo_int, convert_decimal_to_evo_int_for_contract
from app.internal.billing_account_manager.billing_account_manager import get_or_create_billing_account
from app.internal.models import User
from app.pkg.postgresql import get_session


async def withdraw_money(user: User, amount, uow: 'SqlAlchemyUnitOfWork' = Depends(get_uow)) -> Tuple[bool, str]:
    if amount < decimal.Decimal(0.00000001):
        return False, "Too small amount"
    print("user:", user)
    billing_account = await get_or_create_billing_account(user=user, uow=uow)

    transaction_block = await freeze_user_money(uow=uow, user_id=user.id, amount=amount)

    if not transaction_block:
        return False, "Not enough money"
    async with uow:
        withdraw_request = WithdrawRequest(account_id=billing_account.id, amount=amount,
                                           status=WITHDRAW_REQUEST_STATUS_CHOICES_ENUM.IN_PROGRESS,
                                           transaction_block_id=transaction_block.id)
        uow.withdraw_request_actions.add(withdraw_request)
        await uow.session.commit()
        await uow.session.refresh(withdraw_request)
        await withdraw_money_to_address(user.ethereum_ID, convert_decimal_to_evo_int_for_contract(amount))
    return True, "Ok"


async def withdraw_all_money(user, uow: 'SqlAlchemyUnitOfWork' = Depends(get_uow)) -> Tuple[bool, str]:
    data = await get_or_create_billing_account(user=user, uow=uow)

    return await withdraw_money(user, data.balance, uow)
