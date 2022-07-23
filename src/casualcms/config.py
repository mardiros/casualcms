from typing import Sequence

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    from casualcms.service.messagebus import MessageRegistry
    from casualcms.service.unit_of_work import AbstractUnitOfWork

    # Jinja2 config
    template_search_path: str = Field(...)

    import_models: Sequence[str] = Field([])

    # HTTP server Config
    bind: str = "0.0.0.0:8000"
    use_reloader: bool = False

    # create an account on startup
    admin_password: str = ""
    """Set it to create an account"""
    admin_username: str = "admin"
    admin_email: str = "root@localhost"

    # Bootstrap config
    unit_of_work: str | AbstractUnitOfWork = (
        "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork"
    )
    messagebus: MessageRegistry | None = None

    class Config:  # type: ignore
        env_prefix = "casualcms_"
