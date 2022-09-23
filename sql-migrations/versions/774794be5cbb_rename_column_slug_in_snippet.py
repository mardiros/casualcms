"""Rename column slug in snippet

Revision ID: 774794be5cbb
Revises:
Create Date: 2022-09-23 07:08:09.661182

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "774794be5cbb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("idx_snippets_slug", table_name="snippets")
    op.alter_column("snippets", "slug", new_column_name="key")
    op.create_index("idx_snippets_key", "snippets", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_snippets_key", table_name="snippets")
    op.alter_column("snippets", "key", new_column_name="slug")
    op.create_index("idx_snippets_slug", "snippets", ["slug"], unique=False)
