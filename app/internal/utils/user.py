from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import greenlet_spawn
from app.internal.utils.enums import *
from app.internal.models import User, BillingAccount, Transaction, TransactionBlock
from app.pkg.postgresql import get_session
from app.internal.utils.exceptions import NotEnoughMoneyException


async def add_money_to_user(user_id: int, amount: float, transaction_type: TRANSACTION_TYPE_CHOICES_ENUM,
                            db: AsyncSession = Depends(get_session)):
    """Добавление средств на баланс пользователя"""
    query = select(User).filter(User.id == user_id)
    result_query = await db.execute(query)
    user = result_query.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    billing_account = user.billing_account
    if not billing_account:
        billing_account = BillingAccount(user=user)
        db.add(billing_account)
        await db.commit()
        await db.refresh(billing_account)

    balance_after_transaction = billing_account.balance
    balance_after_transaction += amount

    new_transaction = Transaction(account=billing_account, amount=amount,
                                  balance_after_transaction=balance_after_transaction, type=transaction_type)
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    billing_account.balance = new_transaction.balance_after_transaction
    await db.commit()

    return user


async def debit_user_money(user_id: int, amount: float, transaction_type: TRANSACTION_TYPE_CHOICES_ENUM,
                           db: AsyncSession = Depends(get_session)):
    """Списание средств с баланса пользователя"""
    query = select(User).filter(User.id == user_id)
    result_query = await db.execute(query)
    user = result_query.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    billing_account = user.billing_account
    if not billing_account:
        billing_account = BillingAccount(user=user)
        db.add(billing_account)
        await db.commit()
        await db.refresh(billing_account)

    balance_after_transaction = billing_account.balance
    balance_after_transaction -= amount

    if balance_after_transaction < 0:
        raise HTTPException(status_code=400, detail="Not enough money")

    new_transaction = Transaction(account=billing_account, amount=amount,
                                  balance_after_transaction=balance_after_transaction, type=transaction_type)
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    billing_account.balance = new_transaction.balance_after_transaction
    await db.commit()

    return new_transaction

    # async def freeze_user_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Выполняет заморозку средств на балансе пользователя"""
    query = select(Transaction).where(Transaction.id == transaction_id)
    result_query = await db.execute(query)
    transaction = result_query.scalar()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.type = TRANSACTION_TYPE_CHOICES_ENUM.FROZEN
    transaction_block = TransactionBlock(transaction_id=transaction.id)
    print(transaction_block)
    db.add(transaction_block)
    await db.commit()
    await db.refresh(transaction)

    return {'transaction': transaction, 'transaction_block': transaction_block}


async def unfreeze_user_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Выполняет разморозку замороженных средств на балансе пользователя"""
    query = select(Transaction).where(Transaction.id == transaction_id)
    result_query = await db.execute(query)
    transaction = result_query.scalar()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.type = TRANSACTION_TYPE_CHOICES_ENUM.UNFROZEN
    query_transaction_block = select(TransactionBlock).where(TransactionBlock.transaction_id == transaction_id)
    result_query_transaction_block = await db.execute(query_transaction_block)
    transaction_block = result_query_transaction_block.scalar()
    if transaction_block:
        await db.delete(transaction_block)
    await db.commit()

    return {'transaction': transaction, 'transaction_block': transaction_block}


async def freeze_user_money(user_id: int, amount: float,
                            db: AsyncSession = Depends(get_session)) -> TransactionBlock | None:
    try:
        freeze_transaction = await debit_user_money(user_id, amount, TRANSACTION_TYPE_CHOICES_ENUM.FROZEN, db)
        transaction_block = TransactionBlock(transaction_id=freeze_transaction.id)
        db.add(transaction_block)
        await db.commit()
        await db.refresh(transaction_block)
        return transaction_block
    except NotEnoughMoneyException as e:
        return None

    # async def unfreeze_user_money(transaction_block: TransactionBlock) -> Transaction:
    copied_transaction_block = deepcopy(transaction_block)
    amount = copied_transaction_block.transaction.amount

    unfroze_transaction = add_money_to_billing_account(billing_account=transaction_block.transaction.account,
                                                       amount=abs(amount),
                                                       transaction_type=TransactionTypeChoices.UNFROZEN)

    transaction_block.delete()

    return unfroze_transaction
