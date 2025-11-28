from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    # Source information
    source_url = Column(String(1000), unique=True, nullable=False, index=True)
    source_name = Column(String(200), nullable=False)

    # Publication info
    published_at = Column(DateTime(timezone=True), nullable=True)
    author = Column(String(200), nullable=True)

    # Media
    images = Column(JSON, default=list)  # List of image URLs
    attachments = Column(JSON, default=list)  # List of file attachments

    # Categorization
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, default=list)

    # Status
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Metadata
    view_count = Column(Integer, default=0)
    content_hash = Column(String(64), unique=True, index=True)  # For deduplication

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<News(id={self.id}, title={self.title[:50]})>"
