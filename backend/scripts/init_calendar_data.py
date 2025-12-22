#!/usr/bin/env python3
"""
Initialize calendar data with sample semester information.
This script populates the database with the 2025-2026 academic year calendar.

Usage:
    cd /home/laixin/projects/cms-whut/backend
    source venv/bin/activate
    python scripts/init_calendar_data.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, timedelta
from app.core.database import SessionLocal
from app.models.calendar import Semester, SemesterWeek


def generate_weeks(start_date: date, num_weeks: int, semester_id: int):
    """Generate week data for a semester"""
    weeks = []
    current_date = start_date

    for week_num in range(1, num_weeks + 1):
        week_end = current_date + timedelta(days=6)

        week = SemesterWeek(
            semester_id=semester_id,
            week_number=week_num,
            start_date=current_date,
            end_date=week_end,
            is_holiday=False,
            is_exam_week=False
        )
        weeks.append(week)
        current_date = week_end + timedelta(days=1)

    return weeks


def init_2025_2026_first_semester(db):
    """Initialize 2025-2026 First Semester (Fall 2025)"""
    print("Creating 2025-2026 First Semester...")

    semester = Semester(
        name="2025-2026学年第一学期",
        academic_year="2025-2026",
        semester_number=1,
        start_date=date(2025, 9, 1),  # September 1, 2025
        end_date=date(2026, 1, 17),   # January 17, 2026
        is_current=False,
        calendar_source_url="http://i.whut.edu.cn/xl/202507/t20250702_615624.shtml"
    )
    db.add(semester)
    db.flush()

    # Generate 20 weeks
    weeks = generate_weeks(date(2025, 9, 1), 20, semester.id)

    # Mark National Day holiday (Week 5: Oct 1-7, 2025)
    weeks[4].notes = "国庆节假期"
    weeks[4].is_holiday = True

    # Mark exam weeks (Weeks 19-20)
    weeks[18].notes = "期末考试周"
    weeks[18].is_exam_week = True
    weeks[19].notes = "期末考试周"
    weeks[19].is_exam_week = True

    db.add_all(weeks)
    print(f"  ✓ Created {len(weeks)} weeks for Fall 2025 semester")


def init_2025_2026_second_semester(db):
    """Initialize 2025-2026 Second Semester (Spring 2026)"""
    print("Creating 2025-2026 Second Semester...")

    semester = Semester(
        name="2025-2026学年第二学期",
        academic_year="2025-2026",
        semester_number=2,
        start_date=date(2026, 2, 23),  # February 23, 2026
        end_date=date(2026, 7, 5),     # July 5, 2026
        is_current=True,  # Set as current semester
        calendar_source_url="http://i.whut.edu.cn/xl/202512/t20251212_623068.shtml"
    )
    db.add(semester)
    db.flush()

    # Generate 19 weeks
    weeks = generate_weeks(date(2026, 2, 23), 19, semester.id)

    # Mark Qingming Festival holiday (Week 6: around Apr 5)
    weeks[5].notes = "清明节假期"
    weeks[5].is_holiday = True

    # Mark Labor Day holiday (Week 10: May 1-3)
    weeks[9].notes = "劳动节假期"
    weeks[9].is_holiday = True

    # Mark Dragon Boat Festival (Week 15: around June)
    weeks[14].notes = "端午节假期"
    weeks[14].is_holiday = True

    # Mark exam weeks (Weeks 18-19)
    weeks[17].notes = "期末考试周"
    weeks[17].is_exam_week = True
    weeks[18].notes = "期末考试周"
    weeks[18].is_exam_week = True

    db.add_all(weeks)
    print(f"  ✓ Created {len(weeks)} weeks for Spring 2026 semester")


def main():
    """Main function to initialize calendar data"""
    db = SessionLocal()

    try:
        print("\n" + "=" * 60)
        print("Initializing Calendar Data for 2025-2026 Academic Year")
        print("=" * 60 + "\n")

        # Check if data already exists
        existing = db.query(Semester).filter(
            Semester.academic_year == "2025-2026"
        ).first()

        if existing:
            print("⚠️  Calendar data for 2025-2026 already exists!")
            response = input("Do you want to delete and recreate? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return

            # Delete existing data
            print("\nDeleting existing 2025-2026 data...")
            db.query(Semester).filter(
                Semester.academic_year == "2025-2026"
            ).delete()
            db.commit()
            print("  ✓ Deleted existing data\n")

        # Initialize semesters
        init_2025_2026_first_semester(db)
        init_2025_2026_second_semester(db)

        # Commit all changes
        db.commit()

        print("\n" + "=" * 60)
        print("✓ Calendar data initialized successfully!")
        print("=" * 60)
        print("\nSummary:")
        print("  • 2025-2026 First Semester: Sep 1, 2025 - Jan 17, 2026 (20 weeks)")
        print("  • 2025-2026 Second Semester: Feb 23, 2026 - Jul 5, 2026 (19 weeks)")
        print("\nHolidays marked:")
        print("  • National Day (First Semester, Week 5)")
        print("  • Qingming Festival (Second Semester, Week 6)")
        print("  • Labor Day (Second Semester, Week 10)")
        print("  • Dragon Boat Festival (Second Semester, Week 15)")
        print("\nExam weeks marked:")
        print("  • First Semester: Weeks 19-20")
        print("  • Second Semester: Weeks 18-19")
        print("\n" + "=" * 60)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
