import decimal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter

from app.internal.utils.user import freeze_user_money
from app.internal.utils.enums import WITHDRAW_REQUEST_STATUS_CHOICES_ENUM
from app.internal.models import WithdrawRequest, BillingAccount
from app.internal.utils.billig_controls import withdraw_money_to_address
from utils.blockchain_utils import convert_decimal_to_evo_int, convert_decimal_to_evo_int_for_contract
from app.internal.utils.services import get_or_create_billing_account
from app.internal.models import User
from app.pkg.postgresql import get_session


async def withdraw_money(user: User, amount, db: AsyncSession = Depends(get_session)) -> tuple(bool, str):
    if amount < decimal.Decimal(0.00000001):
        return False, "Too small amount"

    billing_account = await get_or_create_billing_account(user_id=user.id)

    transaction_block = freeze_user_money(user.id, amount)

    if not transaction_block:
        return False, "Not enough money"

    withdraw_request = WithdrawRequest(account_id=billing_account.id, amount = amount, status= WITHDRAW_REQUEST_STATUS_CHOICES_ENUM.IN_PROGRESS, transaction_block_id=transaction_block.id)
    db.add(withdraw_request)
    await db.commit()
    await db.refresh()

    withdraw_money_to_address(user.ethereum_ID, convert_decimal_to_evo_int_for_contract(amount))
    return True, "Ok"


async def withdraw_all_money(user, db: AsyncSession = Depends(get_session)) -> tuple(bool, str):
    billing_account = await get_or_create_billing_account(user_id=user.id)

    return withdraw_money(user, billing_account.balance, db)