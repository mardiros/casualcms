"""Remove useless column

Revision ID: dcb958336595
Revises: 0e3023c341fb
Create Date: 2022-10-01 19:53:29.421463

"""
import citext  # type: ignore
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dcb958336595"
down_revision = "0e3023c341fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("pages", "template")


def downgrade() -> None:
    op.add_column(
        "pages",
        sa.Column("template", citext.CIText, autoincrement=False, nullable=False),
    )
