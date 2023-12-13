from fastapi import HTTPException

from app.internal.billing_account_manager.billing_account_manager import get_or_create_billing_account
from app.internal.models import Transaction
from app.internal.user_manager.user_manager import get_user
from app.internal.utils.enums import TRANSACTION_TYPE_CHOICES_ENUM


async def debit_user_money(user_id: int, amount: float, transaction_type: TRANSACTION_TYPE_CHOICES_ENUM,
                           uow: 'SqlAlchemyUnitOfWork'):
    """Списание средств с баланса пользователя"""
    user = await get_user('id', user_id, uow)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    billing_account = await get_or_create_billing_account(uow=uow, user=user)
    balance_after_transaction = billing_account.balance
    balance_after_transaction -= amount
    if balance_after_transaction < 0:
        raise HTTPException(status_code=400, detail="Not enough money")

    async with uow:
        new_transaction = Transaction(account=billing_account, amount=1500,
                                      balance_after_transaction=1500, type=transaction_type)
        uow.transaction_actions.add(new_transaction)
        await uow.session.commit()
        await uow.session.refresh(new_transaction)
        billing_account.balance = new_transaction.balance_after_transaction
        await uow.session.commit()

    return new_transaction
