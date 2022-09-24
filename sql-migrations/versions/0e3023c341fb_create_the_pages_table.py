"""Create the pages table

Revision ID: 0e3023c341fb
Revises: 774794be5cbb
Create Date: 2022-09-24 10:31:13.758848

"""
from alembic import op
import sqlalchemy as sa

import casualcms.adapters.uow_sqla.orm_types
import citext  # type: ignore

# revision identifiers, used by Alembic.
revision = "0e3023c341fb"
down_revision = "774794be5cbb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pages",
        sa.Column("id", casualcms.adapters.uow_sqla.orm_types.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column(
            "site_id", casualcms.adapters.uow_sqla.orm_types.UUID(), nullable=False
        ),
        sa.Column(
            "draft_id", casualcms.adapters.uow_sqla.orm_types.UUID(), nullable=True
        ),
        sa.Column("type", sa.String(length=72), nullable=False),
        sa.Column("template", citext.CIText, nullable=False),
        sa.Column("path", citext.CIText, nullable=False),
        sa.Column("title", citext.CIText, nullable=False),
        sa.Column("body", casualcms.adapters.uow_sqla.orm_types.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["draft_id"], ["drafts.id"], name="fk_pages_draft_id"),
        sa.ForeignKeyConstraint(["site_id"], ["sites.id"], name="fk_pages_site_id"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("pages")
