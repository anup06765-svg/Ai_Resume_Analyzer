"""add jd match & combined score to resumes

Revision ID: 7fa212914959
Revises: 5565977423cc
Create Date: 2026-07-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fa212914959'
down_revision: Union[str, Sequence[str], None] = '5565977423cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('resumes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('jd_match_score', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('jd_matched_skills', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('jd_missing_skills', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('combined_score', sa.Integer(), nullable=True))

    # Existing resumes: combined_score fallback = current ats_score
    op.execute("UPDATE resumes SET combined_score = COALESCE(ats_score, 0)")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('resumes', schema=None) as batch_op:
        batch_op.drop_column('combined_score')
        batch_op.drop_column('jd_missing_skills')
        batch_op.drop_column('jd_matched_skills')
        batch_op.drop_column('jd_match_score')