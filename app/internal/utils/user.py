from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import greenlet_spawn

from app.internal.models import User, BillingAccount, Transaction, TransactionBlock
from app.pkg.postgresql import get_session


async def add_money_to_user(user_id: int, amount: float, transaction_type: str, db: AsyncSession = Depends(get_session)):
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


async def debit_user_money(user_id: int, amount: float, transaction_type: str, db: AsyncSession = Depends(get_session)):
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

    return user


async def freeze_user_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
    """Выполняет заморозку средств на балансе пользователя"""
    query = select(Transaction).where(Transaction.id == transaction_id)
    result_query = await db.execute(query)
    transaction = result_query.scalar()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.type = 'FROZEN'
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

    transaction.type = 'UNFROZEN'
    query_transaction_block = select(TransactionBlock).where(TransactionBlock.transaction_id == transaction_id)
    result_query_transaction_block = await db.execute(query_transaction_block)
    transaction_block = result_query_transaction_block.scalar()
    if transaction_block:
        await db.delete(transaction_block)
    await db.commit()

    return {'transaction': transaction, 'transaction_block': transaction_block}
