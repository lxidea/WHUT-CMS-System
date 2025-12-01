from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User
from app.models.news import News
from app.schemas.user import UserCreate, UserInDB, Token, UserLogin
from app.schemas.news import NewsResponse

router = APIRouter(prefix="/api/auth")

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/bookmarks/{news_id}", status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    news_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a news item to user's bookmarks"""
    # Check if news exists
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News item not found"
        )

    # Check if already bookmarked
    if news in current_user.bookmarks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="News already bookmarked"
        )

    # Add bookmark
    current_user.bookmarks.append(news)
    db.commit()

    return {"message": "Bookmark added successfully"}

@router.delete("/bookmarks/{news_id}", status_code=status.HTTP_200_OK)
async def remove_bookmark(
    news_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a news item from user's bookmarks"""
    # Check if news exists
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News item not found"
        )

    # Check if bookmarked
    if news not in current_user.bookmarks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not in bookmarks"
        )

    # Remove bookmark
    current_user.bookmarks.remove(news)
    db.commit()

    return {"message": "Bookmark removed successfully"}

@router.get("/bookmarks", response_model=List[NewsResponse])
async def get_bookmarks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's bookmarked news items"""
    # Refresh to get latest bookmarks
    db.refresh(current_user)
    return current_user.bookmarks
