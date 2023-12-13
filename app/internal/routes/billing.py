from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.internal.dependencies.uow import get_uow
from app.internal.transaction_manager.transaction_manager import debit_user_money
# from app.internal.utils.user import add_money_to_user, debit_user_money, freeze_user_money, unfreeze_user_money
from app.internal.user_manager.user_manager import check_auth_user
from app.internal.utils.billig_controls import withdraw_all_money
from app.internal.utils.oauth import register_oauth
from app.internal.utils.enums import TRANSACTION_TYPE_CHOICES_ENUM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(
    prefix='/backend/api/v1/billing'
)
oauth = register_oauth()


# @router.post("/add_money/{user_id}")
# async def add_money(user_id: int, amount: float, transaction_type: TRANSACTION_TYPE_CHOICES_ENUM,
#                     db: AsyncSession = Depends(get_session)):
#     """Добавление денег пользователю"""
#     return await add_money_to_user(user_id, amount, transaction_type, db)
#
#
# @router.post("/debit_money/{user_id}")
# async def debit_money(user_id: int, amount: float, transaction_type: TRANSACTION_TYPE_CHOICES_ENUM,
#                       uow: AsyncSession = Depends(get_uow)):
#     """Списание средств с баланса пользователя"""
#     return await debit_user_money(user_id, -amount, transaction_type, uow)


#
#
# @router.post("/freeze_money/{transaction_id}")
# async def freeze_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
#     """Заморозка средств пользователя"""
#     return await freeze_user_money(transaction_id, db)
#
#
# @router.post("/unfreeze_money/{transaction_id}")
# async def unfreeze_money(transaction_id: int, db: AsyncSession = Depends(get_session)):
#     """Разморозка средств пользователя"""
#     return await unfreeze_user_money(transaction_id, db)
#

@router.post('/create_withdraw_request/')
async def create_withdraw_request(uow: AsyncSession = Depends(get_uow), token: str = Depends(oauth2_scheme), ):
    user = await check_auth_user(token=token, uow=uow)
    result, message = await withdraw_all_money(user, uow=uow)
    return {''}
