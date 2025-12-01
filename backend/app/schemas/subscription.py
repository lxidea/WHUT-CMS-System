from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.subscription import NotificationFrequency, EmailStatus


# Keyword Subscription Schemas
class KeywordSubscriptionBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=100, description="Keyword to subscribe to")
    frequency: NotificationFrequency = Field(default=NotificationFrequency.INSTANT, description="Notification frequency")


class KeywordSubscriptionCreate(KeywordSubscriptionBase):
    """Schema for creating a new keyword subscription"""
    pass


class KeywordSubscriptionUpdate(BaseModel):
    """Schema for updating a keyword subscription"""
    is_active: Optional[bool] = None
    frequency: Optional[NotificationFrequency] = None


class KeywordSubscriptionResponse(KeywordSubscriptionBase):
    """Schema for keyword subscription response"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Notification History Schemas
class NotificationHistoryResponse(BaseModel):
    """Schema for notification history response"""
    id: int
    user_id: int
    subscription_id: Optional[int]
    news_id: int
    email_status: EmailStatus
    error_message: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Bulk operations
class KeywordSubscriptionBulkCreate(BaseModel):
    """Schema for creating multiple keyword subscriptions at once"""
    keywords: list[str] = Field(..., min_items=1, max_items=20, description="List of keywords to subscribe to")
    frequency: NotificationFrequency = Field(default=NotificationFrequency.INSTANT)


class KeywordSubscriptionList(BaseModel):
    """Schema for paginated keyword subscription list"""
    total: int
    items: list[KeywordSubscriptionResponse]
    page: int = 1
    page_size: int = 20


class NotificationHistoryList(BaseModel):
    """Schema for paginated notification history list"""
    total: int
    items: list[NotificationHistoryResponse]
    page: int = 1
    page_size: int = 20
