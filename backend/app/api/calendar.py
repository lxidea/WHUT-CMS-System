from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from calendar import monthrange
from app.core.database import get_db
from app.models.calendar import Semester, SemesterWeek
from app.schemas.calendar import (
    SemesterCreate, SemesterUpdate, Semester as SemesterSchema,
    SemesterWithWeeks, SemesterWeekCreate, SemesterWeek as SemesterWeekSchema,
    CalendarSummary
)

router = APIRouter(prefix="/api/calendar")


# ============ Calendar Summary Endpoints ============

@router.get("/summary", response_model=CalendarSummary)
async def get_calendar_summary(db: Session = Depends(get_db)):
    """
    Get current calendar summary for sidebar display
    Includes: current semester, current week, upcoming holidays/exams
    """
    today = datetime.now().date()

    # Get current semester (check is_current flag first, then date range)
    current_semester = db.query(Semester).filter(Semester.is_current == True).first()

    if not current_semester:
        # Fallback to date-based lookup
        current_semester = db.query(Semester).filter(
            and_(
                Semester.start_date <= today,
                Semester.end_date >= today
            )
        ).first()

    if not current_semester:
        return CalendarSummary(
            current_semester=None,
            current_week=None,
            upcoming_holidays=[],
            upcoming_exams=[]
        )

    # Get current week (check if today is within semester dates)
    current_week = None
    if current_semester.is_active:
        current_week = db.query(SemesterWeek).filter(
            and_(
                SemesterWeek.semester_id == current_semester.id,
                SemesterWeek.start_date <= today,
                SemesterWeek.end_date >= today
            )
        ).first()

    # Get upcoming holidays (all holidays in the semester, or next 4 weeks from today)
    if current_semester.is_active:
        upcoming_holidays = db.query(SemesterWeek).filter(
            and_(
                SemesterWeek.semester_id == current_semester.id,
                SemesterWeek.is_holiday == True,
                SemesterWeek.start_date >= today,
                SemesterWeek.start_date <= today + timedelta(weeks=4)
            )
        ).order_by(SemesterWeek.start_date).limit(3).all()
    else:
        # Show all holidays for future semesters
        upcoming_holidays = db.query(SemesterWeek).filter(
            and_(
                SemesterWeek.semester_id == current_semester.id,
                SemesterWeek.is_holiday == True
            )
        ).order_by(SemesterWeek.start_date).limit(3).all()

    # Get upcoming exams (all exams in the semester, or next 8 weeks from today)
    if current_semester.is_active:
        upcoming_exams = db.query(SemesterWeek).filter(
            and_(
                SemesterWeek.semester_id == current_semester.id,
                SemesterWeek.is_exam_week == True,
                SemesterWeek.start_date >= today,
                SemesterWeek.start_date <= today + timedelta(weeks=8)
            )
        ).order_by(SemesterWeek.start_date).limit(3).all()
    else:
        # Show all exam weeks for future semesters
        upcoming_exams = db.query(SemesterWeek).filter(
            and_(
                SemesterWeek.semester_id == current_semester.id,
                SemesterWeek.is_exam_week == True
            )
        ).order_by(SemesterWeek.start_date).limit(3).all()

    return CalendarSummary(
        current_semester=current_semester,
        current_week=current_week,
        upcoming_holidays=upcoming_holidays,
        upcoming_exams=upcoming_exams
    )


@router.get("/monthly")
async def get_monthly_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get monthly calendar view with all weeks, holidays, and exams
    """
    today = datetime.now().date()

    # Default to current month if not specified
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # Get current semester
    current_semester = db.query(Semester).filter(Semester.is_current == True).first()

    if not current_semester:
        # Fallback to date-based lookup
        current_semester = db.query(Semester).filter(
            and_(
                Semester.start_date <= today,
                Semester.end_date >= today
            )
        ).first()

    if not current_semester:
        return {
            "year": year,
            "month": month,
            "month_name": datetime(year, month, 1).strftime("%B"),
            "semester": None,
            "days": []
        }

    # Get first and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Get all weeks that overlap with this month
    weeks = db.query(SemesterWeek).filter(
        and_(
            SemesterWeek.semester_id == current_semester.id,
            SemesterWeek.start_date <= last_day,
            SemesterWeek.end_date >= first_day
        )
    ).order_by(SemesterWeek.week_number).all()

    # Build day-by-day data
    days = []
    current_date = first_day

    while current_date <= last_day:
        # Find which week this day belongs to
        week_info = None
        for week in weeks:
            if week.start_date <= current_date <= week.end_date:
                week_info = {
                    "week_number": week.week_number,
                    "is_holiday": week.is_holiday,
                    "is_exam_week": week.is_exam_week,
                    "notes": week.notes
                }
                break

        days.append({
            "date": current_date.isoformat(),
            "day": current_date.day,
            "weekday": current_date.weekday(),  # 0=Monday, 6=Sunday
            "is_today": current_date == today,
            "week_info": week_info
        })

        current_date += timedelta(days=1)

    return {
        "year": year,
        "month": month,
        "month_name": datetime(year, month, 1).strftime("%B"),
        "semester": {
            "id": current_semester.id,
            "name": current_semester.name,
            "academic_year": current_semester.academic_year
        } if current_semester else None,
        "days": days
    }


# ============ Semester Endpoints ============

@router.get("/semesters", response_model=List[SemesterSchema])
async def get_semesters(
    academic_year: Optional[str] = None,
    is_current: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all semesters
    """
    query = db.query(Semester)

    if academic_year:
        query = query.filter(Semester.academic_year == academic_year)

    if is_current is not None:
        query = query.filter(Semester.is_current == is_current)

    semesters = query.order_by(Semester.start_date.desc()).all()
    return semesters


@router.get("/semesters/current", response_model=SemesterWithWeeks)
async def get_current_semester(db: Session = Depends(get_db)):
    """
    Get current active semester with all weeks
    """
    today = datetime.now().date()

    semester = db.query(Semester).filter(
        and_(
            Semester.start_date <= today,
            Semester.end_date >= today
        )
    ).first()

    if not semester:
        raise HTTPException(status_code=404, detail="No active semester found")

    return semester


@router.get("/semesters/{semester_id}", response_model=SemesterWithWeeks)
async def get_semester_by_id(
    semester_id: int,
    db: Session = Depends(get_db)
):
    """
    Get semester by ID with all weeks
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()

    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    return semester


@router.post("/semesters", response_model=SemesterSchema, status_code=201)
async def create_semester(
    semester_data: SemesterCreate,
    db: Session = Depends(get_db)
):
    """
    Create new semester with optional weeks
    """
    # If setting as current, unset other current semesters
    if semester_data.semester_number:  # Will be set as current by default
        db.query(Semester).update({Semester.is_current: False})

    # Extract weeks data before creating semester
    weeks_data = semester_data.weeks
    semester_dict = semester_data.model_dump(exclude={'weeks'})

    # Create semester
    semester = Semester(**semester_dict)
    db.add(semester)
    db.flush()  # Get the ID

    # Add weeks if provided
    if weeks_data:
        for week_data in weeks_data:
            week = SemesterWeek(semester_id=semester.id, **week_data.model_dump())
            db.add(week)

    db.commit()
    db.refresh(semester)

    return semester


@router.patch("/semesters/{semester_id}", response_model=SemesterSchema)
async def update_semester(
    semester_id: int,
    semester_data: SemesterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update semester information
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()

    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    # If setting this as current, unset others
    if semester_data.is_current:
        db.query(Semester).filter(Semester.id != semester_id).update({Semester.is_current: False})

    for field, value in semester_data.model_dump(exclude_unset=True).items():
        setattr(semester, field, value)

    db.commit()
    db.refresh(semester)

    return semester


@router.delete("/semesters/{semester_id}", status_code=204)
async def delete_semester(
    semester_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete semester and all associated weeks
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()

    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    db.delete(semester)
    db.commit()

    return None


# ============ Semester Week Endpoints ============

@router.get("/semesters/{semester_id}/weeks", response_model=List[SemesterWeekSchema])
async def get_semester_weeks(
    semester_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all weeks for a specific semester
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    weeks = db.query(SemesterWeek).filter(
        SemesterWeek.semester_id == semester_id
    ).order_by(SemesterWeek.week_number).all()

    return weeks


@router.post("/semesters/{semester_id}/weeks", response_model=SemesterWeekSchema, status_code=201)
async def create_semester_week(
    semester_id: int,
    week_data: SemesterWeekCreate,
    db: Session = Depends(get_db)
):
    """
    Add a week to a semester
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")

    week = SemesterWeek(semester_id=semester_id, **week_data.model_dump())
    db.add(week)
    db.commit()
    db.refresh(week)

    return week


@router.get("/weeks/{week_id}", response_model=SemesterWeekSchema)
async def get_week_by_id(
    week_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific week by ID
    """
    week = db.query(SemesterWeek).filter(SemesterWeek.id == week_id).first()

    if not week:
        raise HTTPException(status_code=404, detail="Week not found")

    return week


@router.delete("/weeks/{week_id}", status_code=204)
async def delete_week(
    week_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific week
    """
    week = db.query(SemesterWeek).filter(SemesterWeek.id == week_id).first()

    if not week:
        raise HTTPException(status_code=404, detail="Week not found")

    db.delete(week)
    db.commit()

    return None
