from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class NotificationFrequency(str, enum.Enum):
    """Notification frequency options"""
    INSTANT = "instant"  # Send immediately when matched
    DAILY = "daily"      # Send daily digest
    WEEKLY = "weekly"    # Send weekly digest


class EmailStatus(str, enum.Enum):
    """Email delivery status"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class KeywordSubscription(Base):
    """User keyword subscriptions for email notifications"""
    __tablename__ = "keyword_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    keyword = Column(String, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    frequency = Column(SQLEnum(NotificationFrequency), default=NotificationFrequency.INSTANT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    notifications = relationship("NotificationHistory", back_populates="subscription", cascade="all, delete-orphan")


class NotificationHistory(Base):
    """Track email notifications sent to users"""
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("keyword_subscriptions.id"), nullable=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, index=True)
    email_status = Column(SQLEnum(EmailStatus), default=EmailStatus.PENDING, index=True)
    error_message = Column(String, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")
    subscription = relationship("KeywordSubscription", back_populates="notifications")
    news = relationship("News")
