import asyncio
from logging.config import fileConfig
import ssl
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.configuration.settings import settings
from alembic import context
from config import DB_NAME, DB_USERNAME, DB_PORT, DB_PASSWORD

from sqlalchemy.ext.asyncio import create_async_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
# print(f'{settings.db_port=}')
# print(f'{settings.db_username=}')
# print(f'{settings.db_name=}')
# print(f'{settings.db_password=}')
# config.set_section_option(section, "DB_PORT", DB_PORT)
# config.set_section_option(section, "DB_USERNAME", DB_USERNAME)
# config.set_section_option(section, "DB_NAME", DB_NAME)
# config.set_section_option(section, "DB_PASSWORD", DB_PASSWORD)
# config.set_section_option(section, "DB_PORT", settings.db_port)
# config.set_section_option(section, "DB_USERNAME", settings.db_username)
# config.set_section_option(section, "DB_NAME", settings.db_name)
# config.set_section_option(section, "DB_PASSWORD", settings.db_password)

config.set_section_option('alembic',
                          'sqlalchemy.url',
                          (f'postgresql+asyncpg://{settings.db_username}:{settings.db_password}@{settings.db_host}:'
                           f'{settings.db_port}/{settings.db_name}?async_fallback=True')
                          )

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
from app.internal.models.base import Base

# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()



async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    ca_path = "app/certs/ca-certificate.crt"
    my_ssl_context = ssl.create_default_context(cafile=ca_path)
    my_ssl_context.verify_mode = ssl.CERT_REQUIRED

    # ssl_args = {'ssl_ca': ca_path} 
    ssl_args = {'ssl': {'ca': ca_path}}
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    if settings.is_prod == "true":
        connectable = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"ssl": my_ssl_context})
    else:
        connectable = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)


    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
