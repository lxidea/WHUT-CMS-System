"""add_keyword_subscriptions_and_notifications

Revision ID: d3844a6b4068
Revises: a5ab5d420995
Create Date: 2025-11-30 21:41:57.441567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3844a6b4068'
down_revision: Union[str, None] = 'a5ab5d420995'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create keyword_subscriptions table
    op.create_table(
        'keyword_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('keyword', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('frequency', sa.Enum('instant', 'daily', 'weekly', name='notificationfrequency'), nullable=True, server_default='instant'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_keyword_subscriptions_id'), 'keyword_subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_keyword_subscriptions_is_active'), 'keyword_subscriptions', ['is_active'], unique=False)
    op.create_index(op.f('ix_keyword_subscriptions_keyword'), 'keyword_subscriptions', ['keyword'], unique=False)
    op.create_index(op.f('ix_keyword_subscriptions_user_id'), 'keyword_subscriptions', ['user_id'], unique=False)

    # Create notification_history table
    op.create_table(
        'notification_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('email_status', sa.Enum('pending', 'sent', 'failed', name='emailstatus'), nullable=True, server_default='pending'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['keyword_subscriptions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_history_email_status'), 'notification_history', ['email_status'], unique=False)
    op.create_index(op.f('ix_notification_history_id'), 'notification_history', ['id'], unique=False)
    op.create_index(op.f('ix_notification_history_news_id'), 'notification_history', ['news_id'], unique=False)
    op.create_index(op.f('ix_notification_history_subscription_id'), 'notification_history', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_notification_history_user_id'), 'notification_history', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop notification_history table
    op.drop_index(op.f('ix_notification_history_user_id'), table_name='notification_history')
    op.drop_index(op.f('ix_notification_history_subscription_id'), table_name='notification_history')
    op.drop_index(op.f('ix_notification_history_news_id'), table_name='notification_history')
    op.drop_index(op.f('ix_notification_history_id'), table_name='notification_history')
    op.drop_index(op.f('ix_notification_history_email_status'), table_name='notification_history')
    op.drop_table('notification_history')

    # Drop keyword_subscriptions table
    op.drop_index(op.f('ix_keyword_subscriptions_user_id'), table_name='keyword_subscriptions')
    op.drop_index(op.f('ix_keyword_subscriptions_keyword'), table_name='keyword_subscriptions')
    op.drop_index(op.f('ix_keyword_subscriptions_is_active'), table_name='keyword_subscriptions')
    op.drop_index(op.f('ix_keyword_subscriptions_id'), table_name='keyword_subscriptions')
    op.drop_table('keyword_subscriptions')

    # Drop enum types
    op.execute('DROP TYPE notificationfrequency')
    op.execute('DROP TYPE emailstatus')
