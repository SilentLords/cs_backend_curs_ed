from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__: str = 'users'

    id: Column = Column(Integer, autoincrement=True, primary_key=True, index=True)
    openid: Column = Column(String, unique=True)
    nickname: Column = Column(String, unique=True)
    ethereum_ID: Column = Column(String, unique=True)
    billing_model: Column = Column(Integer, ForeignKey("billing.id"))


class Billing(Base):
    __tablename__: str = "billing"
    id: Column = Column(Integer, autoincrement=True, primary_key=True, index=True)
    banned: Column = Column(Boolean, default=True)
    money_count: Column = Column(Float, default=0)
    # owner: Column = Column("User", back_populates="items", nullable=True)
