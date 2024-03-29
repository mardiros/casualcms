from typing import Sequence

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="casualcms_")

    # Jinja2 config
    template_search_path: str = Field(...)

    # Page models
    import_models: Sequence[str] = Field([])

    assets_path: str = Field("")

    # HTTP server Config
    bind: str = "0.0.0.0:8000"
    use_reloader: bool = False

    # create an account on startup
    admin_password: str = ""
    """Set it to create an account"""
    admin_username: str = "admin"
    admin_email: str = "root@localhost"

    # Bootstrap config
    unit_of_work: str | AbstractUnitOfWork = "casualcms.adapters.uow_sqla:SQLUnitOfWork"
    database_url: str = "postgresql+asyncpg://postgres@postgresql/casualcms"
    create_database_schema: bool = False
    database_migration_cfg: str = "/srv/casualcms/alembic.ini"

    messagebus: MessageRegistry | None = None
