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
    Column("username", CIText, nullable=False),  # type: ignore
    Column("password", String(60), nullable=False),
    Column("email", CIText, nullable=False),  # type: ignore
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
        "user_id",
        UUID,
        ForeignKey("accounts.id", name="fk_authn_tokens_user_id"),
    ),
    Column("expires_at", DateTime(), nullable=False),
    Column("client_addr", IpAddress(), nullable=False),
    Column("user_agent", CIText, nullable=False),  # type: ignore
    Index("idx_authn_tokens_token", "token", unique=True),
    Index("idx_authn_tokens_user_id", "user_id", unique=False),
    Index("idx_authn_tokens_client_addr", "client_addr", unique=False),
    Index("idx_authn_tokens_expires_at", "expires_at", unique=False),
    Index("idx_authn_tokens_created_at", "created_at", unique=False),
)


drafts = Table(
    "drafts",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column("type", String(72), nullable=False),
    Column("slug", CIText, nullable=False),  # type: ignore
    Column("title", CIText, nullable=False),  # type: ignore
    Column("description", CIText, nullable=False),  # type: ignore
    Column("body", JSON, nullable=False),
    Index("idx_drafts_type", "type", unique=False),
    Index("idx_drafts_slug", "slug", unique=False),
    Index("idx_drafts_created_at", "created_at", unique=False),
)

drafts_treepath = Table(
    "drafts_treepath",
    metadata,
    Column(
        "ancestor_id",
        UUID,
        ForeignKey("drafts.id", name="fk_drafts_ancestor_id"),
        primary_key=True,
    ),
    Column(
        "descendant_id",
        UUID,
        ForeignKey("drafts.id", name="fk_drafts_descendant_id"),
        primary_key=True,
    ),
    Column("length", Integer),
    Index(
        "idx_drafts_treepath_descendant_id",
        "descendant_id",
        "length",
        unique=False,
    ),
)

snippets = Table(
    "snippets",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column("type", String(72), nullable=False),
    Column("key", CIText, nullable=False),  # type: ignore
    Column("body", JSON, nullable=False),
    Index("idx_snippets_type", "type", unique=False),
    Index("idx_snippets_key", "key", unique=True),
    Index("idx_snippets_created_at", "created_at", unique=False),
)


sites = Table(
    "sites",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column(
        "draft_id",
        UUID,
        ForeignKey("drafts.id", name="fk_sites_draft_id"),
        nullable=False,
    ),
    Column("hostname", String(253)),
    Column("default", Boolean, nullable=False),
    Column("secure", Boolean, nullable=False),
    Index("idx_sites_draft_id", "draft_id", unique=False),
    Index("idx_sites_created_at", "created_at", unique=False),
    Index("idx_sites_hostname", "hostname", unique=True),
)


settings = Table(
    "settings",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column("key", String(72), nullable=False),
    Column(
        "site_id",
        UUID,
        ForeignKey("sites.id", name="fk_settings_site_id"),
        nullable=False,
    ),
    Column("value", JSON, nullable=False),
    Index("idx_settings_key_site_id", "key", "site_id", unique=True),
    Index("idx_settings_created_at", "created_at", unique=False),
)

pages = Table(
    "pages",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("created_at", DateTime(), nullable=False),
    Column(
        "site_id",
        UUID,
        ForeignKey("sites.id", name="fk_pages_site_id"),
        nullable=False,
    ),
    Column(
        "draft_id",
        UUID,
        ForeignKey("drafts.id", name="fk_pages_draft_id"),
        nullable=True,
    ),
    Column("type", String(72), nullable=False),
    Column("path", CIText, nullable=False),  # type: ignore
    Column("title", CIText, nullable=False),  # type: ignore
    Column("body", JSON, nullable=False),
)
