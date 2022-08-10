"""SQLAlchemy schema."""

from casualcms.domain.model import AccountStatus

from .orm_types import (
    JSON,
    UUID,
    Boolean,
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


pages = Table(
    "pages",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column("type", String(72), nullable=False),
    Column("slug", CIText, nullable=False),
    Column("title", CIText, nullable=False),
    Column("description", CIText, nullable=False),
    Column("body", JSON, nullable=False),
    Index("idx_pages_type", "type", unique=False),
    Index("idx_pages_slug", "slug", unique=False),
    Index("idx_pages_created_at", "created_at", unique=False),
)

pages_treepath = Table(
    "pages_treepath",
    metadata,
    Column(
        "ancestor_id",
        UUID,
        ForeignKey("pages.id", name="fk_pages_ancestor_id"),
        primary_key=True,
    ),
    Column(
        "descendant_id",
        UUID,
        ForeignKey("pages.id", name="fk_pages_descendant_id"),
        primary_key=True,
    ),
    Column("length", Integer),
    Index(
        "idx_pages_treepath_descendant_id",
        "descendant_id",
        "length",
        unique=False,
    ),
)


sites = Table(
    "sites",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column(
        "page_id",
        UUID,
        ForeignKey("pages.id", name="fk_sites_page_id"),
        nullable=False,
    ),
    Column("hostname", String(253), primary_key=True),
    Column("default", Boolean, nullable=False),
    Index("idx_sites_page_id", "page_id", unique=False),
    Index("idx_sites_created_at", "created_at", unique=False),
    Index("idx_sites_hostname", "hostname", unique=True),
)
