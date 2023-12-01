from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, MetaData, Table, DateTime, func
from sqlalchemy.orm import relationship
from app.internal.utils.enums import TRANSACTION_TYPE_CHOICES_ENUM, WITHDRAW_REQUEST_STATUS_CHOICES_ENUM
from .user import User
from .base import Base, ChoiceType
from sqlalchemy.dialects.postgresql import ENUM as PgEnum


class BillingAccount(Base):
    __tablename__ = 'billing_account'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    balance = Column(Float, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    withdraw_request = relationship('WithdrawRequest', back_populates='account')

    user = relationship('User', back_populates='billing_account')
    transactions = relationship(
        'Transaction', back_populates='account', cascade='all, delete-orphan', lazy='joined'
    )

    def __repr__(self):
        return f"<BillingAccount(id={self.id}, user_id={self.user_id}," \
               f"balance={self.balance}, created_at={self.created_at})>"


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('billing_account.id'))
    amount = Column(Float, default=0, nullable=False)
    balance_after_transaction = Column(Float, default=0, nullable=False)
    type = Column(PgEnum(TRANSACTION_TYPE_CHOICES_ENUM, name='transaction_type', create_type=False), nullable=False, default=TRANSACTION_TYPE_CHOICES_ENUM.EMPTY)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    account = relationship('BillingAccount', back_populates='transactions')
    transaction_block = relationship(
        'TransactionBlock', uselist=False, back_populates='transaction'
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, account_id={self.account_id}, amount={self.amount}, " \
               f"balance_after_transaction={self.balance_after_transaction}, type={self.type}, " \
               f"created_at={self.created_at})>"


class TransactionBlock(Base):
    __tablename__ = 'transaction_block'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(Integer, ForeignKey('transaction.id', ondelete='CASCADE'))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    withdraw_request = relationship('WithdrawRequest', back_populates='transaction_block')

    transaction = relationship('Transaction', back_populates='transaction_block')

    def __repr__(self):
        return f"<TransactionBlock(id={self.id}, transaction_id={self.transaction_id}, created_at={self.created_at})>"



class WithdrawRequest(Base):
    __tablename__ = 'withdraw_request'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    account = relationship('BillingAccount', back_populates='withdraw_request')
    account_id = Column(Integer, ForeignKey('billing_account.id'))

    amount = Column(Float, default=0, nullable=False )
    tx_hash = Column(String(length=255), nullable=True)
    status = Column(PgEnum(WITHDRAW_REQUEST_STATUS_CHOICES_ENUM, name='withdraw_request_type', create_type=False), nullable=False, default=WITHDRAW_REQUEST_STATUS_CHOICES_ENUM.EMPTY)
    transaction_block = relationship('TransactionBlock', back_populates='withdraw_request')
    transaction_block_id = Column(Integer, ForeignKey('transaction_block.id'))


    def __repr__(self):
        return f"<WithdrawRequest(account_id={self.account_id},amount={self.amount}, status={self.status}>"



class WithdrawCheck(Base):
    __tablename__ = 'withdraw_check'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    tx_hash = Column(String(length=255), nullable=False)
    tx_blockNumber = Column(String(length=255), nullable=False)
    tx_from = Column(String(length=255), nullable=False)
    tx_to = Column(String(length=255), nullable=False)
    created_at = Column(String(length=255), nullable=False)


    def __repr__(self):
        return f"<WithdrawCheck(tx_hash={self.tx_hash}>"

