from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from app.configuration.settings import Settings
import ssl 



settings = Settings()
ca_path = "app/certs/ca-certificate.crt"

my_ssl_context = ssl.create_default_context(cafile=ca_path)
my_ssl_context.verify_mode = ssl.CERT_REQUIRED

# ssl_args = {'ssl_ca': ca_path} 
ssl_args = {'ssl': {'ca': ca_path}}
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

if settings.is_prod == "true":
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"ssl": my_ssl_context}, pool_size=20, max_overflow=0)
else:
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_size=20, max_overflow=0)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)





# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

async def create_session() -> AsyncSession:
    async with async_session() as session:
        return session

