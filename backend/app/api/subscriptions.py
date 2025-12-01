from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.subscription import KeywordSubscription, NotificationHistory
from app.schemas.subscription import (
    KeywordSubscriptionCreate,
    KeywordSubscriptionUpdate,
    KeywordSubscriptionResponse,
    KeywordSubscriptionBulkCreate,
    KeywordSubscriptionList,
    NotificationHistoryList
)
from app.core.security import get_current_user

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.post("/", response_model=KeywordSubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription: KeywordSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new keyword subscription for the current user
    """
    # Check if keyword already exists for this user
    existing = db.query(KeywordSubscription).filter(
        and_(
            KeywordSubscription.user_id == current_user.id,
            KeywordSubscription.keyword == subscription.keyword.strip().lower()
        )
    ).first()

    if existing:
        # Reactivate if exists but inactive
        if not existing.is_active:
            existing.is_active = True
            existing.frequency = subscription.frequency
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You already have an active subscription for keyword '{subscription.keyword}'"
            )

    # Create new subscription
    db_subscription = KeywordSubscription(
        user_id=current_user.id,
        keyword=subscription.keyword.strip().lower(),
        frequency=subscription.frequency
    )

    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)

    return db_subscription


@router.post("/bulk", response_model=List[KeywordSubscriptionResponse], status_code=status.HTTP_201_CREATED)
def create_bulk_subscriptions(
    bulk_create: KeywordSubscriptionBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create multiple keyword subscriptions at once
    """
    created_subscriptions = []

    for keyword in bulk_create.keywords:
        keyword_clean = keyword.strip().lower()

        # Skip if already exists
        existing = db.query(KeywordSubscription).filter(
            and_(
                KeywordSubscription.user_id == current_user.id,
                KeywordSubscription.keyword == keyword_clean
            )
        ).first()

        if not existing:
            db_subscription = KeywordSubscription(
                user_id=current_user.id,
                keyword=keyword_clean,
                frequency=bulk_create.frequency
            )
            db.add(db_subscription)
            created_subscriptions.append(db_subscription)
        elif not existing.is_active:
            # Reactivate
            existing.is_active = True
            existing.frequency = bulk_create.frequency
            created_subscriptions.append(existing)

    db.commit()

    for sub in created_subscriptions:
        db.refresh(sub)

    return created_subscriptions


@router.get("/", response_model=KeywordSubscriptionList)
def get_my_subscriptions(
    page: int = 1,
    page_size: int = 20,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's keyword subscriptions
    """
    query = db.query(KeywordSubscription).filter(
        KeywordSubscription.user_id == current_user.id
    )

    if active_only:
        query = query.filter(KeywordSubscription.is_active == True)

    # Get total count
    total = query.count()

    # Paginate
    subscriptions = query.order_by(
        KeywordSubscription.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "items": subscriptions,
        "page": page,
        "page_size": page_size
    }


@router.get("/{subscription_id}", response_model=KeywordSubscriptionResponse)
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific subscription by ID
    """
    subscription = db.query(KeywordSubscription).filter(
        and_(
            KeywordSubscription.id == subscription_id,
            KeywordSubscription.user_id == current_user.id
        )
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    return subscription


@router.patch("/{subscription_id}", response_model=KeywordSubscriptionResponse)
def update_subscription(
    subscription_id: int,
    update_data: KeywordSubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a keyword subscription
    """
    subscription = db.query(KeywordSubscription).filter(
        and_(
            KeywordSubscription.id == subscription_id,
            KeywordSubscription.user_id == current_user.id
        )
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    # Update fields
    if update_data.is_active is not None:
        subscription.is_active = update_data.is_active

    if update_data.frequency is not None:
        subscription.frequency = update_data.frequency

    db.commit()
    db.refresh(subscription)

    return subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a keyword subscription
    """
    subscription = db.query(KeywordSubscription).filter(
        and_(
            KeywordSubscription.id == subscription_id,
            KeywordSubscription.user_id == current_user.id
        )
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    db.delete(subscription)
    db.commit()

    return None


@router.post("/{subscription_id}/unsubscribe", status_code=status.HTTP_200_OK)
def unsubscribe_from_keyword(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe from a keyword (public endpoint for email links)
    Note: This doesn't require authentication to allow unsubscribe from email
    """
    subscription = db.query(KeywordSubscription).filter(
        KeywordSubscription.id == subscription_id
    ).first()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    subscription.is_active = False
    db.commit()

    return {"message": f"Successfully unsubscribed from keyword '{subscription.keyword}'"}


@router.get("/history/", response_model=NotificationHistoryList)
def get_notification_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification history for current user
    """
    query = db.query(NotificationHistory).filter(
        NotificationHistory.user_id == current_user.id
    )

    total = query.count()

    notifications = query.order_by(
        NotificationHistory.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "items": notifications,
        "page": page,
        "page_size": page_size
    }
