from fastapi import HTTPException
from starlette.responses import JSONResponse

from app.internal.models import GiftEvent
from app.internal.billing_account_manager.billing_account_manager import get_or_create_billing_account
from app.internal.dependencies.uow import get_uow_for_celery
from app.internal.models import Transaction
from app.internal.user_manager.user_manager import get_user
from app.internal.utils.enums import TRANSACTION_TYPE_CHOICES_ENUM, GIFT_EVENT_STATUS_CHOICES_ENUM
from app.internal.utils.services import getting_list_best_players


async def add_money_to_user(user_id: int, amount: float, transaction_type: TRANSACTION_TYPE_CHOICES_ENUM,
                            uow: 'SqlAlchemyUnitOfWork'):
    """Добавление средств на баланс пользователя"""
    user = await get_user('id', user_id, uow)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    billing_account = await get_or_create_billing_account(uow=uow, user=user)
    balance_after_transaction = billing_account.balance
    balance_after_transaction += amount

    async with uow:
        new_transaction = Transaction(account=billing_account, amount=amount,
                                      balance_after_transaction=balance_after_transaction, type=transaction_type)
        uow.transaction_actions.add(new_transaction)
        await uow.session.commit()
        await uow.session.refresh(new_transaction)
        billing_account.balance = new_transaction.balance_after_transaction
        await uow.session.commit()

    return user


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
        new_transaction = Transaction(account=billing_account, amount=amount,
                                      balance_after_transaction=balance_after_transaction, type=transaction_type)
        uow.transaction_actions.add(new_transaction)
        await uow.session.commit()
        await uow.session.refresh(new_transaction)
        billing_account.balance = new_transaction.balance_after_transaction
        await uow.session.commit()

    return new_transaction


async def prize_distribution(gift_event: GiftEvent, ):
    uow = get_uow_for_celery()
    """Функция начисляет призовые деньги"""
    offset = 0
    limit = 4
    get_latest = False
    print('There 1')
    awards = [gift_event.top_one_count, gift_event.top_two_count, gift_event.top_three_count, gift_event.top_four_count]
    try:
        top_players = await getting_list_best_players(offset, limit, get_latest,
                                                      leaderboard_id=gift_event.leaderboard_id)
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Ошибка получения лидерборда")
    print('There2')
    list_nic = []
    list_of_awarded_users = []

    # достаём никнеймы лидеров турнирной таблицы
    for gamer in top_players:
        nickname = gamer["player"]["nickname"]
        list_nic.append(nickname)
    print(list_nic)
    print("PLAYERS: ", list_nic)
    for index, amount in enumerate(awards):
        user = await get_user('nickname', field_value=list_nic[index], uow=uow)
        if not user:
            continue
        user_id = user.id
        transaction_type = TRANSACTION_TYPE_CHOICES_ENUM.GIFT
        amount = float(amount)
        print(awards)
        try:
            awarded_user = await add_money_to_user(user_id, amount, transaction_type, uow)
        except Exception as ex:
            raise HTTPException(status_code=500, detail="Ошибка начисления средств")
        list_of_awarded_users.append(awarded_user)
    # gift_event.status = GIFT_EVENT_STATUS_CHOICES_ENUM.DONE
    async with uow:
        gift_event = await uow.gift_event_actions.get_first_by_field('id', gift_event.id)
        uow.gift_event_actions.update(gift_event, {"status": GIFT_EVENT_STATUS_CHOICES_ENUM.DONE})
        await uow.session.commit()
    return JSONResponse(content={'detail': f'Пользователи {list_nic} получили призовые'})
