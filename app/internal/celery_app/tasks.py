import asyncio

from celery import shared_task
from app.internal.models import WithdrawCheck, User
from app.internal.utils.bscscan import get_transactions
from app.configuration import settings

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import greenlet_spawn

from app.internal.models import User, BillingAccount, Transaction, TransactionBlock
from app.internal.utils.services import prize_distribution
from app.pkg.postgresql import get_session


@shared_task()
def hello_world():
    print("Hello, world!")


@shared_task()
def distribute_gifts():
    # Todo: список ниже
    # 1. Получить GiftEvent сегодняшней даты
    # 2. если ивент есть и статус в прогрессе то выполняем
    # 3. Ставим GiftEvent`у статус Done
    result = prize_distribution()
    asyncio.run(result)




@shared_task(name="update_withdraw_request_statuses", once={'graceful': True})
def update_withdraw_request_statuses():
    db = get_session()
    def get_lastblock():

        query = select(User).filter(User.id == user_id)
        result_query = db.execute(query)
        user = result_query.scalar()
        last_blocknumber = WithdrawCheck.objects.order_by('tx_blockNumber').last()
        if last_blocknumber:
            return last_blocknumber.tx_blockNumber
        return 0

    startblock = get_lastblock()

    token_txs = get_transactions(settings.CORPORATE_PAYOUTS_CONTRACT_ADDRESS, startblock)

    for e in token_txs:
        if not WithdrawCheck.objects.filter(tx_hash__iexact=e['hash']).exists():
            WithdrawCheck.objects.create(tx_hash=e['hash'],
                                      tx_from=e['from'],
                                      tx_to=e['to'],
                                      tx_blockNumber=e['blockNumber'])
            if User.objects.filter(web3_address__iexact=e['to']).exists():
                user = User.objects.get(web3_address__iexact=e['to'])
                billing_account, _ = BillingAccount.objects.get_or_create(user=user)
                amount = convert_blockchain_value_to_decimal(e['value'])
                if WithdrawRequest.objects.filter(account=billing_account,
                                                  status=WithdrawRequestStatusChoices.IN_PROGRESS,
                                                  amount=amount).exists():
                    withdraw_request = WithdrawRequest.objects.filter(account=billing_account,
                                                  status=WithdrawRequestStatusChoices.IN_PROGRESS,
                                                  amount=amount).last()
                    convert_freeze_to_transaction(withdraw_request.transaction_block)
                    withdraw_request.status = WithdrawRequestStatusChoices.DONE
                    withdraw_request.transaction_block = None
                    withdraw_request.tx_hash = e['hash']
                    withdraw_request.save()
                    print(f"Withdraw request done: {e['hash']}")
                else:
                    print(f"Withdraw request not found: {e['hash']}")
            else:
                print(f"Unknown user: {e['hash']}")
        else:
            print(f"Transaction already checked: {e['hash']}")