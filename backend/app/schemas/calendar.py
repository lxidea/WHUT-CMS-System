from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


# ============ Semester Week Schemas ============

class SemesterWeekBase(BaseModel):
    """Base schema for semester week"""
    week_number: int = Field(..., ge=1, le=30, description="Week number (1-30)")
    start_date: date = Field(..., description="Week start date")
    end_date: date = Field(..., description="Week end date")
    notes: Optional[str] = Field(None, max_length=500, description="Week notes (holidays, exams, etc.)")
    is_holiday: bool = Field(False, description="Is this a holiday week?")
    is_exam_week: bool = Field(False, description="Is this an exam week?")


class SemesterWeekCreate(SemesterWeekBase):
    """Schema for creating a semester week"""
    pass


class SemesterWeekUpdate(BaseModel):
    """Schema for updating a semester week"""
    week_number: Optional[int] = Field(None, ge=1, le=30)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=500)
    is_holiday: Optional[bool] = None
    is_exam_week: Optional[bool] = None


class SemesterWeek(SemesterWeekBase):
    """Schema for semester week in responses"""
    id: int
    semester_id: int
    is_current: bool = Field(..., description="Is this the current week?")

    class Config:
        from_attributes = True


# ============ Semester Schemas ============

class SemesterBase(BaseModel):
    """Base schema for semester"""
    name: str = Field(..., max_length=100, description="Semester name")
    academic_year: str = Field(..., max_length=20, description="Academic year (e.g., 2025-2026)")
    semester_number: int = Field(..., ge=1, le=2, description="Semester number (1 or 2)")
    start_date: date = Field(..., description="Semester start date")
    end_date: date = Field(..., description="Semester end date")
    calendar_image_url: Optional[str] = Field(None, max_length=500, description="Calendar image URL")
    calendar_source_url: Optional[str] = Field(None, max_length=500, description="Source page URL")


class SemesterCreate(SemesterBase):
    """Schema for creating a semester"""
    weeks: Optional[List[SemesterWeekCreate]] = Field(None, description="Week information")


class SemesterUpdate(BaseModel):
    """Schema for updating a semester"""
    name: Optional[str] = Field(None, max_length=100)
    academic_year: Optional[str] = Field(None, max_length=20)
    semester_number: Optional[int] = Field(None, ge=1, le=2)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    calendar_image_url: Optional[str] = Field(None, max_length=500)
    calendar_source_url: Optional[str] = Field(None, max_length=500)


class Semester(SemesterBase):
    """Schema for semester in responses"""
    id: int
    is_current: bool = Field(..., description="Is this the current semester?")
    is_active: bool = Field(..., description="Is this semester currently active based on dates?")
    current_week: int = Field(..., description="Current week number (0 if not active)")
    created_at: date
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True


class SemesterWithWeeks(Semester):
    """Schema for semester with all week details"""
    weeks: List[SemesterWeek] = Field(..., description="List of weeks in this semester")

    class Config:
        from_attributes = True


# ============ Calendar Summary Schemas ============

class CalendarSummary(BaseModel):
    """Summary of current calendar information for sidebar display"""
    current_semester: Optional[Semester] = Field(None, description="Current active semester")
    current_week: Optional[SemesterWeek] = Field(None, description="Current week information")
    upcoming_holidays: List[SemesterWeek] = Field([], description="Upcoming holiday weeks")
    upcoming_exams: List[SemesterWeek] = Field([], description="Upcoming exam weeks")

    class Config:
        from_attributes = True
