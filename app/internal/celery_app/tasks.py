import asyncio
import datetime

from celery import shared_task
from app.internal.models import WithdrawCheck, User
from app.internal.models.gifts import GiftEvent
from app.internal.utils.bscscan import get_transactions
from app.configuration import settings

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import greenlet_spawn
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import cast, Date
from app.configuration.settings import Settings
import ssl

from app.internal.models import User, BillingAccount, Transaction, TransactionBlock
from app.internal.utils.services import prize_distribution
from app.pkg.postgresql import get_session
from app.internal.utils.enums import GIFT_EVENT_STATUS_CHOICES_ENUM
from sqlalchemy.ext.asyncio import AsyncSession, async_session

settings = Settings()


@shared_task()
def hello_world():
    print("Hello, world!")


async def create_session(a_session):
    async with a_session() as session:
        return session


@shared_task()
def distribute_gifts():
    ca_path = "app/certs/ca-certificate.crt"
    my_ssl_context = ssl.create_default_context(cafile=ca_path)
    my_ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_args = {'ssl': {'ca': ca_path}}
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    if settings.is_prod == "true":
        engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"ssl": my_ssl_context})
    else:
        engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    session = asyncio.run(create_session(async_session))
    gift = select(GiftEvent).filter(GiftEvent.start_at == datetime.date.today())
    print(datetime.date.today())
    print("tut req:", gift)
    result_query = asyncio.run(session.execute(gift))
    gift = result_query.scalar()
    print("This is:", gift)
    if gift:
        if gift.status == GIFT_EVENT_STATUS_CHOICES_ENUM.IN_PROGRESS:
            print("Start send Gifts")
            result = prize_distribution(gift)
            asyncio.run(result)



# @shared_task(name="update_withdraw_request_statuses", once={'graceful': True})
# def update_withdraw_request_statuses():
#     db = get_session()
#
#     def get_lastblock():
#
#         query = select(User).filter(User.id == user_id)
#         result_query = db.execute(query)
#         user = result_query.scalar()
#         last_blocknumber = WithdrawCheck.objects.order_by('tx_blockNumber').last()
#         if last_blocknumber:
#             return last_blocknumber.tx_blockNumber
#         return 0
#
#     startblock = get_lastblock()
#
#     token_txs = get_transactions(settings.CORPORATE_PAYOUTS_CONTRACT_ADDRESS, startblock)
#
#     for e in token_txs:
#         if not WithdrawCheck.objects.filter(tx_hash__iexact=e['hash']).exists():
#             WithdrawCheck.objects.create(tx_hash=e['hash'],
#                                          tx_from=e['from'],
#                                          tx_to=e['to'],
#                                          tx_blockNumber=e['blockNumber'])
#             if User.objects.filter(web3_address__iexact=e['to']).exists():
#                 user = User.objects.get(web3_address__iexact=e['to'])
#                 billing_account, _ = BillingAccount.objects.get_or_create(user=user)
#                 amount = convert_blockchain_value_to_decimal(e['value'])
#                 if WithdrawRequest.objects.filter(account=billing_account,
#                                                   status=WithdrawRequestStatusChoices.IN_PROGRESS,
#                                                   amount=amount).exists():
#                     withdraw_request = WithdrawRequest.objects.filter(account=billing_account,
#                                                                       status=WithdrawRequestStatusChoices.IN_PROGRESS,
#                                                                       amount=amount).last()
#                     convert_freeze_to_transaction(withdraw_request.transaction_block)
#                     withdraw_request.status = WithdrawRequestStatusChoices.DONE
#                     withdraw_request.transaction_block = None
#                     withdraw_request.tx_hash = e['hash']
#                     withdraw_request.save()
#                     print(f"Withdraw request done: {e['hash']}")
#                 else:
#                     print(f"Withdraw request not found: {e['hash']}")
#             else:
#                 print(f"Unknown user: {e['hash']}")
#         else:
#             print(f"Transaction already checked: {e['hash']}")
