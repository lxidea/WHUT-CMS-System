from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class NewsBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source_url: str
    source_name: str
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    images: List[str] = []
    attachments: List[dict] = []
    category: Optional[str] = None
    tags: List[str] = []

class NewsCreate(NewsBase):
    content_hash: str

class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None

class NewsResponse(NewsBase):
    id: int
    is_published: bool
    is_featured: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NewsList(BaseModel):
    total: int
    items: List[NewsResponse]
    page: int
    page_size: int
