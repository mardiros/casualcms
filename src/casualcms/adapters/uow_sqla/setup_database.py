from alembic import command
from alembic.config import Config
from sqlalchemy import text  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine  # type: ignore

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


async def create_database_schema(settings: Settings, engine: AsyncEngine) -> None:

    async with engine.begin() as conn:  # type: ignore
        try:
            # Find a better alternative
            await conn.execute(text("select * from alembic_version"))
        except Exception:
            database_exists = False
        else:
            database_exists = True

    async with engine.begin() as conn:  # type: ignore
        if database_exists:
            upgrade_alembic(settings)
        else:
            if settings.database_url.startswith("postgresql+asyncpg://"):
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
            await conn.run_sync(orm.metadata.create_all)
            stamp_alembic(settings)
