from datetime import datetime, timedelta
from typing import Any, Mapping

from pydantic import Field

from casualcms.utils import generate_id, generate_secret

from .base import Command, Metadata


class CreateAccount(Command):
    username: str = Field(...)
    password: str = Field(...)
    email: str = Field(...)
    lang: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(
        category="user", name="create_account", schemaVersion=1
    )


class CreateAccountCipheredPassword(Command):
    username: str = Field(...)
    password: str = Field(...)
    email: str = Field(...)
    lang: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(
        category="user", name="create_account", schemaVersion=1
    )


class CreateAuthnToken(Command):
    user_id: str = Field(...)  # UUID
    user_agent: str = Field(...)
    client_addr: str = Field(...)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(minutes=30)
    )
    created_at: datetime = Field(default_factory=datetime.now, exclude=True)
    id: str = Field(default_factory=generate_id)
    token: str = Field(default_factory=generate_secret)
    metadata: Metadata = Metadata(category="user", name="authenticate", schemaVersion=1)


class DeleteAuthnToken(Command):
    token: str = Field(default_factory=generate_secret)
    user_id: str = Field(...)  # UUID
    user_agent: str = Field(...)
    client_addr: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(category="user", name="logout", schemaVersion=1)


class CreatePage(Command):
    type: str = Field(...)
    payload: Mapping[str, Any] = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(category="page", name="create_page", schemaVersion=1)


class UpdatePage(Command):
    id: str = Field(...)
    payload: Mapping[str, Any] = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Metadata = Metadata(category="page", name="update_page", schemaVersion=1)


class PublishPage(Command):
    id: str = Field(...)
    site_id: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Metadata = Metadata(category="page", name="publish_page", schemaVersion=1)


class DeletePage(Command):
    id: str = Field(...)
    deleted_at: datetime = Field(default_factory=datetime.now)
    path: str = Field(...)
    metadata: Metadata = Metadata(category="page", name="delete_page", schemaVersion=1)


class CreateSite(Command):
    id: str = Field(default_factory=generate_id)
    created_at: datetime = Field(default_factory=datetime.now)
    hostname: str = Field(...)
    root_page_path: str = Field(...)
    default: bool = Field(...)
    secure: bool = Field(...)
    metadata: Metadata = Metadata(category="site", name="create_site", schemaVersion=1)


class UpdateSite(Command):
    id: str = Field(default_factory=generate_id)
    hostname: str | None = Field(default=None)
    root_page_path: str | None = Field(default=None)
    default: bool | None = Field(default=None)
    secure: bool | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Metadata = Metadata(category="site", name="create_site", schemaVersion=1)


class DeleteSite(Command):
    id: str = Field(...)
    deleted_at: datetime = Field(default_factory=datetime.now)
    hostname: str = Field(...)
    metadata: Metadata = Metadata(category="site", name="delete_site", schemaVersion=1)


class CreateSnippet(Command):
    type: str = Field(...)
    key: str = Field(...)
    body: Mapping[str, Any] = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(
        category="snippet", name="create_snippet", schemaVersion=1
    )


class UpdateSnippet(Command):
    key: str | None = Field(..., description="New key")
    body: Mapping[str, Any] | None = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(...)
    metadata: Metadata = Metadata(
        category="snippet", name="update_snippet", schemaVersion=1
    )


class DeleteSnippet(Command):
    key: str = Field(...)
    id: str = Field(...)
    metadata: Metadata = Metadata(
        category="snippet", name="update_snippet", schemaVersion=1
    )


class CreateSetting(Command):
    key: str = Field(...)
    hostname: str = Field(...)
    body: Mapping[str, Any] = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(
        category="setting", name="create_setting", schemaVersion=1
    )


class UpdateSetting(Command):
    hostname: str = Field(...)
    key: str = Field(...)
    body: Mapping[str, Any] | None = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(...)
    metadata: Metadata = Metadata(
        category="setting", name="update_setting", schemaVersion=1
    )


class DeleteSetting(Command):
    hostname: str = Field(...)
    key: str = Field(...)
    id: str = Field(...)
    metadata: Metadata = Metadata(
        category="setting", name="update_setting", schemaVersion=1
    )
