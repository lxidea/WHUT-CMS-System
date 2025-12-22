#!/usr/bin/env python3
"""
Automated Calendar Import from WHUT Website

This script automatically:
1. Fetches calendar pages from http://i.whut.edu.cn/xl
2. Downloads calendar images
3. Extracts calendar data using OCR
4. Populates the database with semester and week information

Usage:
    cd /home/laixin/projects/cms-whut/backend
    source venv/bin/activate
    python scripts/auto_import_calendar.py

Options:
    --latest-only    Only import the most recent calendar
    --dry-run        Show what would be imported without actually importing
    --use-gpu        Use GPU for OCR (faster but requires CUDA)
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from app.core.database import SessionLocal
from app.models.calendar import Semester, SemesterWeek
from ocr_calendar_extractor import (
    CalendarOCRExtractor,
    fetch_calendar_page_images,
    fetch_calendar_image_url
)


def semester_exists(db, academic_year: str, semester_number: int) -> bool:
    """Check if semester already exists in database"""
    existing = db.query(Semester).filter(
        Semester.academic_year == academic_year,
        Semester.semester_number == semester_number
    ).first()
    return existing is not None


def import_semester(db, semester_data: dict, weeks_data: list, source_url: str, dry_run: bool = False):
    """Import semester and weeks into database"""
    semester_info = semester_data

    # Check if already exists
    if semester_exists(db, semester_info['academic_year'], semester_info['semester_number']):
        print(f"⚠️  Semester {semester_info['name']} already exists in database")
        response = input("Do you want to update it? (yes/no): ")
        if response.lower() != 'yes':
            print("Skipped.")
            return False

        # Delete existing
        if not dry_run:
            db.query(Semester).filter(
                Semester.academic_year == semester_info['academic_year'],
                Semester.semester_number == semester_info['semester_number']
            ).delete()
            db.commit()
            print("✓ Deleted existing semester data")

    if dry_run:
        print(f"\n[DRY RUN] Would import:")
        print(f"  Semester: {semester_info['name']}")
        print(f"  Weeks: {len(weeks_data)}")
        return True

    # Create semester
    semester = Semester(
        name=semester_info['name'],
        academic_year=semester_info['academic_year'],
        semester_number=semester_info['semester_number'],
        start_date=semester_info['start_date'],
        end_date=semester_info['end_date'],
        is_current=False,  # Don't auto-set as current
        calendar_source_url=source_url
    )
    db.add(semester)
    db.flush()

    # Create weeks
    for week_data in weeks_data:
        week = SemesterWeek(
            semester_id=semester.id,
            week_number=week_data['week_number'],
            start_date=week_data['start_date'],
            end_date=week_data['end_date'],
            notes=week_data.get('notes'),
            is_holiday=week_data.get('is_holiday', False),
            is_exam_week=week_data.get('is_exam_week', False)
        )
        db.add(week)

    db.commit()
    print(f"✓ Imported {semester_info['name']} with {len(weeks_data)} weeks")
    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Automated calendar import from WHUT website')
    parser.add_argument('--latest-only', action='store_true', help='Only import the most recent calendar')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without importing')
    parser.add_argument('--use-gpu', action='store_true', help='Use GPU for OCR processing')
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("WHUT Automated Calendar Import from Website")
    print("=" * 70 + "\n")

    if args.dry_run:
        print("🔍 DRY RUN MODE - No data will be imported\n")

    db = SessionLocal()
    extractor = CalendarOCRExtractor(use_gpu=args.use_gpu)

    try:
        # Step 1: Fetch calendar list
        calendars = fetch_calendar_page_images()

        if not calendars:
            print("❌ No calendars found on website")
            return

        if args.latest_only:
            calendars = calendars[:1]
            print(f"📌 Processing only the latest calendar\n")

        # Step 2: Process each calendar
        imported_count = 0
        for i, calendar in enumerate(calendars, 1):
            print(f"\n{'─' * 70}")
            print(f"Processing [{i}/{len(calendars)}]: {calendar['title']}")
            print(f"{'─' * 70}\n")

            try:
                # Fetch image URL from detail page
                image_url = fetch_calendar_image_url(calendar['detail_url'])

                if not image_url:
                    print("⚠️  No image found, skipping...\n")
                    continue

                # Extract calendar data using OCR
                print("\n🤖 Running OCR extraction...")
                result = extractor.extract_calendar_from_url(image_url)

                semester_data = result['semester']
                weeks_data = result['weeks']

                # Validate extraction
                if not semester_data.get('name') or not weeks_data:
                    print("⚠️  Failed to extract valid calendar data, skipping...\n")
                    print(f"Debug info: semester={semester_data}, weeks count={len(weeks_data)}")
                    continue

                # Display summary
                print("\n📊 Extraction Summary:")
                print(f"  Semester: {semester_data['name']}")
                print(f"  Academic Year: {semester_data['academic_year']}")
                print(f"  Semester Number: {semester_data['semester_number']}")
                print(f"  Start Date: {semester_data['start_date']}")
                print(f"  End Date: {semester_data['end_date']}")
                print(f"  Total Weeks: {len(weeks_data)}")

                # Show holidays and exams
                holidays = [w for w in weeks_data if w['is_holiday']]
                exams = [w for w in weeks_data if w['is_exam_week']]

                if holidays:
                    print(f"\n  Holidays detected ({len(holidays)}):")
                    for h in holidays:
                        print(f"    • Week {h['week_number']}: {h['notes'] or '假期'}")

                if exams:
                    print(f"\n  Exam weeks detected ({len(exams)}):")
                    for e in exams:
                        print(f"    • Week {e['week_number']}: {e['notes'] or '考试周'}")

                # Import to database
                print("\n💾 Importing to database...")
                if import_semester(db, semester_data, weeks_data, calendar['detail_url'], args.dry_run):
                    imported_count += 1

            except Exception as e:
                print(f"\n❌ Error processing calendar: {e}")
                import traceback
                traceback.print_exc()
                print("\nContinuing with next calendar...\n")
                continue

        # Summary
        print("\n" + "=" * 70)
        if args.dry_run:
            print(f"✓ DRY RUN COMPLETE - Would have imported {imported_count} calendar(s)")
        else:
            print(f"✓ IMPORT COMPLETE - Successfully imported {imported_count} calendar(s)")
        print("=" * 70 + "\n")

        # Suggest setting current semester
        if imported_count > 0 and not args.dry_run:
            print("💡 Tip: Don't forget to set the current semester:")
            print("   Use the API: PATCH /api/calendar/semesters/{id} with {\"is_current\": true}")
            print("   Or use the sample script to mark the active semester as current\n")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
