from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine  # type: ignore

from casualcms.config import Settings
from . import orm



def stamp_alembic(settings: Settings):
    if settings.database_url == "sqlite+aiosqlite:///":
        return
    alembic_cfg = Config(settings.database_migration_cfg)
    command.stamp(alembic_cfg, "head")


def upgrade_alembic(settings: Settings):
    if settings.database_url == "sqlite+aiosqlite:///":
        return
    alembic_cfg = Config(settings.database_migration_cfg)
    command.upgrade(alembic_cfg, "head")


async def create_database_schema(settings: Settings, engine: AsyncEngine):
    async with engine.begin() as conn:  # type: ignore
        try:
            await conn.execute("select * from alembic_version")
        except Exception:
            # await conn.execute("create extension if not exists citext")
            await conn.run_sync(orm.metadata.create_all)
            stamp_alembic(settings)
        else:
            upgrade_alembic(settings)
