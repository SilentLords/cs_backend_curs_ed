from app.internal.models import TransactionBlock
from app.internal.transaction_manager.transaction_manager import debit_user_money
from app.internal.utils.enums import TRANSACTION_TYPE_CHOICES_ENUM
from app.internal.utils.exceptions import NotEnoughMoneyException


async def freeze_user_money(user_id: int, amount: float,
                            uow: 'SqlAlchemyUnitOfWork') -> TransactionBlock | None:
    try:
        freeze_transaction = await debit_user_money(user_id, amount, TRANSACTION_TYPE_CHOICES_ENUM.WITHDRAW, uow)
        async with uow:
            transaction_block = TransactionBlock(transaction_id=freeze_transaction.id)
            uow.transaction_block_actions.add(transaction_block)
            await uow.session.commit()
            await uow.session.refresh(transaction_block)
        return transaction_block
    except NotEnoughMoneyException as e:
        return None
