"""SQLAlchemy schema."""

from casualcms.domain.model import AccountStatus

from .orm_types import (
    JSON,
    UUID,
    CIText,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
)

metadata = MetaData()

accounts = Table(
    "accounts",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column("username", CIText, nullable=False),
    Column("password", String(60), nullable=False),
    Column("email", CIText, nullable=False),
    Column("lang", String(8), nullable=False),  # isocode such as fr or zh-Hant
    Column("status", Enum(AccountStatus, name="account_status"), nullable=False),
    Index("idx_users_username", "username", unique=True),
    Index("idx_users_email", "email", unique=True),
    Index("idx_users_created_at", "created_at", unique=False),
)
