from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, MetaData, Table, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

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



