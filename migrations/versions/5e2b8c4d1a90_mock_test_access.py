"""mock test access grants

Adds per-test settings (free or locked) and access grants, and links each test
session to the grant it used. Users who had already started a test keep
unlimited access to every test.

Revision ID: 5e2b8c4d1a90
Revises: 3c1f7a2b9d44
Create Date: 2026-09-26 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app

# `sat` on Supabase/Postgres, None on local SQLite (see DB_SCHEMA in app.py)
SCHEMA = current_app.config.get("DB_SCHEMA")
PREFIX = f"{SCHEMA}." if SCHEMA else ""


# revision identifiers, used by Alembic.
revision = '5e2b8c4d1a90'
down_revision = '3c1f7a2b9d44'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('mock_test_settings',
    sa.Column('practice_test_id', sa.String(length=100), nullable=False),
    sa.Column('is_free', sa.Boolean(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('practice_test_id'),
    schema=SCHEMA
    )
    op.create_table('test_access_grants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('practice_test_id', sa.String(length=100), nullable=True),
    sa.Column('max_attempts', sa.Integer(), nullable=True),
    sa.Column('source', sa.String(length=20), nullable=False),
    sa.Column('note', sa.String(length=255), nullable=True),
    sa.Column('granted_by_user_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=True),
    sa.Column('revoked_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['granted_by_user_id'], [f'{PREFIX}users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], [f'{PREFIX}users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema=SCHEMA
    )
    with op.batch_alter_table('test_access_grants', schema=SCHEMA) as batch_op:
        batch_op.create_index(batch_op.f('ix_test_access_grants_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('test_sessions', schema=SCHEMA) as batch_op:
        batch_op.add_column(sa.Column('access_grant_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_test_sessions_access_grant_id'), ['access_grant_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_test_sessions_access_grant_id', 'test_access_grants',
            ['access_grant_id'], ['id'], referent_schema=SCHEMA,
        )

    # Don't lock out students who were already practicing. The NULLs need casts:
    # under SELECT DISTINCT, Postgres types a bare NULL as text.
    op.execute(f"""
        INSERT INTO {PREFIX}test_access_grants (user_id, practice_test_id, max_attempts, source, note, created_at)
        SELECT DISTINCT user_id, CAST(NULL AS VARCHAR(100)), CAST(NULL AS INTEGER),
               'migration', 'Existing student when access control launched', CURRENT_TIMESTAMP
        FROM {PREFIX}test_sessions
    """)


def downgrade():
    with op.batch_alter_table('test_sessions', schema=SCHEMA) as batch_op:
        batch_op.drop_constraint('fk_test_sessions_access_grant_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_test_sessions_access_grant_id'))
        batch_op.drop_column('access_grant_id')

    with op.batch_alter_table('test_access_grants', schema=SCHEMA) as batch_op:
        batch_op.drop_index(batch_op.f('ix_test_access_grants_user_id'))

    op.drop_table('test_access_grants', schema=SCHEMA)
    op.drop_table('mock_test_settings', schema=SCHEMA)
