"""widen test_sessions.practice_test_id

Test names such as "Digital SAT Mock Test (Oct 2026)" don't fit in 10 chars.

Revision ID: 3c1f7a2b9d44
Revises: 8a8a895e0716
Create Date: 2026-09-26 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app

# `sat` on Supabase/Postgres, None on local SQLite (see DB_SCHEMA in app.py)
SCHEMA = current_app.config.get("DB_SCHEMA")


# revision identifiers, used by Alembic.
revision = '3c1f7a2b9d44'
down_revision = '8a8a895e0716'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('test_sessions', schema=SCHEMA) as batch_op:
        batch_op.alter_column(
            'practice_test_id',
            existing_type=sa.String(length=10),
            type_=sa.String(length=100),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table('test_sessions', schema=SCHEMA) as batch_op:
        batch_op.alter_column(
            'practice_test_id',
            existing_type=sa.String(length=100),
            type_=sa.String(length=10),
            existing_nullable=False,
        )
