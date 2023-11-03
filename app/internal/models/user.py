from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float, MetaData, Table
from app.pkg.postgresql import Base
#test
metadata = MetaData()
users = Table(
    'users',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True, index=True),
    Column('nickname', String, unique=True),
    Column('ethereum_ID', String, unique=True),
    Column('billing_model', Integer, ForeignKey("billing.id"))

)


billing = Table(
    "billing",
    metadata,

    Column('id',Integer, autoincrement=True, primary_key=True, index=True),
    Column('banned',Boolean, default=True),
    Column('money_count',Float, default=0),
    # owner: Column = Column("User", back_populates="items", nullab,le=True)
)