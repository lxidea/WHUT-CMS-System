from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base


class Semester(Base):
    """学期信息表 - Semester Information"""
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    name = Column(String(100), nullable=False)  # e.g., "2025-2026学年第一学期"
    academic_year = Column(String(20), nullable=False, index=True)  # e.g., "2025-2026"
    semester_number = Column(Integer, nullable=False)  # 1 or 2 (first or second semester)

    # Date range
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)

    # Status
    is_current = Column(Boolean, default=False, index=True)  # Only one semester should be current

    # Optional: Link to original calendar image
    calendar_image_url = Column(String(500), nullable=True)
    calendar_source_url = Column(String(500), nullable=True)  # Link to i.whut.edu.cn page

    # Metadata
    created_at = Column(Date, server_default=func.current_date())
    updated_at = Column(Date, onupdate=func.current_date())

    # Relationships
    weeks = relationship("SemesterWeek", back_populates="semester", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Semester(id={self.id}, name={self.name})>"

    @property
    def is_active(self) -> bool:
        """Check if the semester is currently active based on dates"""
        today = datetime.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def current_week(self) -> int:
        """Calculate current week number based on today's date"""
        today = datetime.now().date()
        if not self.is_active:
            return 0

        # Find the week that contains today
        for week in self.weeks:
            if week.start_date <= today <= week.end_date:
                return week.week_number
        return 0


class SemesterWeek(Base):
    """学期周次信息表 - Semester Week Information"""
    __tablename__ = "semester_weeks"

    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False, index=True)

    # Week information
    week_number = Column(Integer, nullable=False)  # 1, 2, 3, ..., 20
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)

    # Optional notes
    notes = Column(Text, nullable=True)  # e.g., "国庆节假期", "期末考试周", "放假"
    is_holiday = Column(Boolean, default=False)  # Mark holiday weeks
    is_exam_week = Column(Boolean, default=False)  # Mark exam weeks

    # Relationships
    semester = relationship("Semester", back_populates="weeks")

    def __repr__(self):
        return f"<SemesterWeek(semester_id={self.semester_id}, week={self.week_number})>"

    @property
    def is_current(self) -> bool:
        """Check if this week is the current week"""
        today = datetime.now().date()
        return self.start_date <= today <= self.end_date
