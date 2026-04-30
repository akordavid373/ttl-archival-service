"""Add synchronization tables

Revision ID: 001
Revises: 
Create Date: 2026-04-29 08:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create sync_jobs table
    op.create_table(
        'sync_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('source_system', sa.String(length=100), nullable=False),
        sa.Column('target_system', sa.String(length=100), nullable=False),
        sa.Column('sync_type', sa.Enum('FULL', 'INCREMENTAL', 'REAL_TIME', name='synctype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'PAUSED', name='syncstatus'), nullable=True),
        sa.Column('conflict_strategy', sa.Enum('LAST_WRITE_WINS', 'SOURCE_WINS', 'TARGET_WINS', 'MANUAL', name='conflictstrategy'), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('records_synced', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('records_failed', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_job_status', 'sync_jobs', ['status'], unique=False)

    # Create sync_records table
    op.create_table(
        'sync_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sync_job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_id', sa.String(length=255), nullable=False),
        sa.Column('record_type', sa.String(length=100), nullable=False),
        sa.Column('source_checksum', sa.String(length=64), nullable=True),
        sa.Column('target_checksum', sa.String(length=64), nullable=True),
        sa.Column('status', sa.Enum('SYNCED', 'CONFLICT', 'FAILED', 'SKIPPED', name='recordsyncstatus'), nullable=False),
        sa.Column('conflict_details', sa.JSON(), nullable=True),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['sync_job_id'], ['sync_jobs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sync_record_job_type', 'sync_records', ['sync_job_id', 'record_type'], unique=False)
    op.create_index(op.f('ix_sync_records_record_id'), 'sync_records', ['record_id'], unique=False)

    # Create sync_conflicts table
    op.create_table(
        'sync_conflicts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sync_job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sync_record_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_data', sa.JSON(), nullable=False),
        sa.Column('target_data', sa.JSON(), nullable=False),
        sa.Column('resolution', sa.String(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['sync_job_id'], ['sync_jobs.id'], ),
        sa.ForeignKeyConstraint(['sync_record_id'], ['sync_records.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('sync_conflicts')
    op.drop_table('sync_records')
    op.drop_table('sync_jobs')
    op.execute('DROP TYPE synctype')
    op.execute('DROP TYPE syncstatus')
    op.execute('DROP TYPE conflictstrategy')
    op.execute('DROP TYPE recordsyncstatus')
