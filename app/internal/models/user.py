from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, MetaData, Table, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__: str = 'users'

    id: Column = Column(Integer, autoincrement=True, primary_key=True, index=True)
    openid: Column = Column(String, unique=True)
    nickname: Column = Column(String, unique=True)
    ethereum_ID: Column = Column(String, unique=True)
    billing_model: Column = Column(Integer, ForeignKey("billing.id"))
    password: Column = Column(String)

    billing_account = relationship(
        'BillingAccount', back_populates='user', uselist=False, cascade='all, delete-orphan', lazy='joined'
    )

    billing_account = relationship(
        'BillingAccount', back_populates='user', uselist=False, cascade='all, delete-orphan', lazy='joined'
    )


class Billing(Base):
    __tablename__: str = "billing"
    id: Column = Column(Integer, autoincrement=True, primary_key=True, index=True)
    banned: Column = Column(Boolean, default=True)
    money_count: Column = Column(Float, default=0)
    # owner: Column = Column("User", back_populates="items", nullable=True)


# Модель для хранения JWT токена
class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    access_token = Column(String, index=True)
    token_type = Column(String)


class BillingAccount(Base):
    __tablename__ = 'billing_account'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    balance = Column(Float, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

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
    type = Column(String(255), nullable=False)
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

    transaction = relationship('Transaction', back_populates='transaction_block')

    def __repr__(self):
        return f"<TransactionBlock(id={self.id}, transaction_id={self.transaction_id}, created_at={self.created_at})>"
