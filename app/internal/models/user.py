from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float
from app.pkg.postgresql import Base


class User(Base):
    __tablename__: str = 'users'

    id: Column = Column(Integer, autoincrement=True, primary_key=True, index=True)
    nickname: Column = Column(String, unique=True)
    ethereum_ID: Column = Column(String, unique=True)
    billing_model: Column = Column(Integer, ForeignKey("billing.id"))


class Billing(Base):
    __tablename__: str = "billing"
    id: Column = Column(Integer, autoincrement=True, primary_key=True, index=True)
    banned: Column = Column(Boolean, default=True)
    money_count: Column = Column(Float, default=0)
    owner: Column = Column("User", back_populates="items", nullable=True)
