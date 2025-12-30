from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional
from app.core.database import get_db
from app.models.news import News
from app.schemas.news import NewsResponse, NewsList, NewsCreate, NewsUpdate

router = APIRouter(prefix="/api/news")

@router.get("/", response_model=NewsList)
async def get_news_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    publisher: Optional[str] = None,
    department: Optional[str] = None,
    source_name: Optional[str] = None,
    search: Optional[str] = None,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get paginated list of news items
    """
    query = db.query(News).filter(News.is_published == True)

    if category:
        query = query.filter(News.category == category)

    if publisher:
        query = query.filter(News.publisher == publisher)

    if department:
        query = query.filter(News.department == department)

    if source_name:
        query = query.filter(News.source_name == source_name)

    if featured_only:
        query = query.filter(News.is_featured == True)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                News.title.ilike(search_filter),
                News.content.ilike(search_filter),
                News.summary.ilike(search_filter)
            )
        )

    total = query.count()

    items = query.order_by(desc(News.published_at)).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return NewsList(
        total=total,
        items=items,
        page=page,
        page_size=page_size
    )

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_by_id(
    news_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single news item by ID and increment view count
    """
    news = db.query(News).filter(News.id == news_id).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    # Increment view count
    news.view_count += 1
    db.commit()

    return news

@router.post("/", response_model=NewsResponse, status_code=201)
async def create_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db)
):
    """
    Create new news item (typically called by spider)
    """
    # Check if news with same content_hash already exists
    existing = db.query(News).filter(News.content_hash == news_data.content_hash).first()
    if existing:
        raise HTTPException(status_code=409, detail="News with this content already exists")

    news = News(**news_data.model_dump())
    db.add(news)
    db.commit()
    db.refresh(news)

    return news

@router.patch("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_data: NewsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update existing news item
    """
    news = db.query(News).filter(News.id == news_id).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    for field, value in news_data.model_dump(exclude_unset=True).items():
        setattr(news, field, value)

    db.commit()
    db.refresh(news)

    return news

@router.delete("/{news_id}", status_code=204)
async def delete_news(
    news_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete news item
    """
    news = db.query(News).filter(News.id == news_id).first()

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    db.delete(news)
    db.commit()

    return None

@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """
    Get list of all unique categories
    """
    categories = db.query(News.category).distinct().filter(
        News.category.isnot(None),
        News.is_published == True
    ).all()

    return {"categories": [cat[0] for cat in categories]}

@router.get("/publishers/list")
async def get_publishers(db: Session = Depends(get_db)):
    """
    Get list of all unique publishers
    """
    publishers = db.query(News.publisher).distinct().filter(
        News.publisher.isnot(None),
        News.is_published == True
    ).all()

    return {"publishers": [pub[0] for pub in publishers]}

@router.get("/departments/list")
async def get_departments(db: Session = Depends(get_db)):
    """
    Get list of all unique departments
    """
    departments = db.query(News.department).distinct().filter(
        News.department.isnot(None),
        News.is_published == True
    ).all()

    return {"departments": [dept[0] for dept in departments]}


@router.get("/sources/list")
async def get_sources(db: Session = Depends(get_db)):
    """
    Get list of all unique news sources
    """
    sources = db.query(News.source_name).distinct().filter(
        News.source_name.isnot(None),
        News.is_published == True
    ).all()

    return {"sources": [src[0] for src in sources]}
