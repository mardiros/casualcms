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
    IpAddress,
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


authn_tokens = Table(
    "authn_tokens",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column("token", String(86), nullable=False),
    Column(
        "account_id",
        UUID,
        ForeignKey("accounts.id", name="fk_authn_tokens_account_id"),
    ),
    Column("expires_at", DateTime(), nullable=False),
    Column("client_addr", IpAddress(), nullable=False),
    Column("user_agent", CIText, nullable=False),
    Index("idx_authn_tokens_token", "token", unique=True),
    Index("idx_authn_tokens_account_id", "account_id", unique=False),
    Index("idx_authn_tokens_client_addr", "client_addr", unique=False),
    Index("idx_authn_tokens_expires_at", "expires_at", unique=False),
    Index("idx_authn_tokens_created_at", "created_at", unique=False),
)
