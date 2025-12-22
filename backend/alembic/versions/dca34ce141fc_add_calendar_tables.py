"""add_calendar_tables

Revision ID: dca34ce141fc
Revises: 6d7914add71c
Create Date: 2025-12-13 01:34:51.146219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dca34ce141fc'
down_revision: Union[str, None] = '6d7914add71c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create semesters table
    op.create_table(
        'semesters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('academic_year', sa.String(length=20), nullable=False),
        sa.Column('semester_number', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True, default=False),
        sa.Column('calendar_image_url', sa.String(length=500), nullable=True),
        sa.Column('calendar_source_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=True),
        sa.Column('updated_at', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_semesters_id'), 'semesters', ['id'], unique=False)
    op.create_index(op.f('ix_semesters_academic_year'), 'semesters', ['academic_year'], unique=False)
    op.create_index(op.f('ix_semesters_start_date'), 'semesters', ['start_date'], unique=False)
    op.create_index(op.f('ix_semesters_end_date'), 'semesters', ['end_date'], unique=False)
    op.create_index(op.f('ix_semesters_is_current'), 'semesters', ['is_current'], unique=False)

    # Create semester_weeks table
    op.create_table(
        'semester_weeks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('week_number', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_holiday', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_exam_week', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_semester_weeks_id'), 'semester_weeks', ['id'], unique=False)
    op.create_index(op.f('ix_semester_weeks_semester_id'), 'semester_weeks', ['semester_id'], unique=False)
    op.create_index(op.f('ix_semester_weeks_start_date'), 'semester_weeks', ['start_date'], unique=False)
    op.create_index(op.f('ix_semester_weeks_end_date'), 'semester_weeks', ['end_date'], unique=False)


def downgrade() -> None:
    # Drop semester_weeks table first (due to foreign key)
    op.drop_index(op.f('ix_semester_weeks_end_date'), table_name='semester_weeks')
    op.drop_index(op.f('ix_semester_weeks_start_date'), table_name='semester_weeks')
    op.drop_index(op.f('ix_semester_weeks_semester_id'), table_name='semester_weeks')
    op.drop_index(op.f('ix_semester_weeks_id'), table_name='semester_weeks')
    op.drop_table('semester_weeks')

    # Drop semesters table
    op.drop_index(op.f('ix_semesters_is_current'), table_name='semesters')
    op.drop_index(op.f('ix_semesters_end_date'), table_name='semesters')
    op.drop_index(op.f('ix_semesters_start_date'), table_name='semesters')
    op.drop_index(op.f('ix_semesters_academic_year'), table_name='semesters')
    op.drop_index(op.f('ix_semesters_id'), table_name='semesters')
    op.drop_table('semesters')
