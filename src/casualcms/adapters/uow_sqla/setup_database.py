from alembic import command
from alembic.config import Config
from sqlalchemy import text  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine  # type: ignore
from sqlalchemy.ext.asyncio.engine import create_async_engine  # type: ignore

from casualcms.config import Settings

from . import orm


def stamp_alembic(settings: Settings) -> None:
    if settings.database_url == "sqlite+aiosqlite:///":
        return
    alembic_cfg = Config(settings.database_migration_cfg)
    command.stamp(alembic_cfg, "head")


def upgrade_alembic(settings: Settings) -> None:
    if settings.database_url == "sqlite+aiosqlite:///":
        return
    alembic_cfg = Config(settings.database_migration_cfg)
    command.upgrade(alembic_cfg, "head")


async def create_database(settings: Settings, engine: AsyncEngine) -> None:
    url = engine.url
    dialect = url.get_dialect().name
    if dialect == "sqlite":
        return
    driver = url.get_driver_name()
    host = url.host
    username = url.username
    password = f":{url.password}" if url.password else ""
    database = url.database
    url = f"{dialect}+{driver}://{username}{password}@{host}/"
    engine = create_async_engine(url, future=True, echo=False)
    async with engine.begin() as conn:  # type: ignore
        await conn.execute(text(f"ROLLBACK"))
        await conn.execute(
            text(f'CREATE DATABASE "{database}" WITH OWNER "{username}"')
        )
        await conn.execute(text(f"BEGIN"))


async def create_database_schema(settings: Settings, engine: AsyncEngine) -> None:


    try:
        database_exists = None
        async with engine.begin() as conn:  # type: ignore
            try:
                # inspect does not work with async engine
                # from sqlalchemy import inspect
                # insp = inspect(engine)
                # print(insp.get_table_names())
                await conn.execute(text("select * from alembic_version"))
            except Exception:
                database_exists = False
            else:
                database_exists = True
    except Exception:
        await create_database(settings, engine)
        database_exists = False

    async with engine.begin() as conn:  # type: ignore
        if database_exists:
            upgrade_alembic(settings)
        else:
            if engine.url.get_dialect().name == "postgresql":
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
            await conn.run_sync(orm.metadata.create_all)
            stamp_alembic(settings)
