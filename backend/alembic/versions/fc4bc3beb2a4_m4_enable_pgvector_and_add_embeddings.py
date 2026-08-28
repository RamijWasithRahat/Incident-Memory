"""M4: enable pgvector and add embeddings

Revision ID: fc4bc3beb2a4
Revises: 27e82d246b27
Create Date: 2026-08-27 18:30:33.192185

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "fc4bc3beb2a4"
down_revision: Union[str, None] = "27e82d246b27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )

    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "document_chunks",
        "embedding",
    )