# Calendar Feature Documentation

## Overview

The calendar feature adds a semester calendar sidebar to the CMS-WHUT system that displays:
- Current semester information
- Current week number
- Upcoming holidays
- Upcoming exam weeks

This helps students and faculty quickly see what week of the semester they're in.

## Components

### Backend

**Database Models** (`backend/app/models/calendar.py`):
- `Semester` - Stores semester information (name, dates, academic year)
- `SemesterWeek` - Stores individual week information with notes, holidays, and exam markers

**API Endpoints** (`backend/app/api/calendar.py`):
- `GET /api/calendar/summary` - Get calendar summary for sidebar (current semester, week, upcoming events)
- `GET /api/calendar/semesters` - List all semesters
- `GET /api/calendar/semesters/current` - Get current active semester with all weeks
- `GET /api/calendar/semesters/{id}` - Get specific semester details
- `POST /api/calendar/semesters` - Create new semester (with weeks)
- `PATCH /api/calendar/semesters/{id}` - Update semester
- `DELETE /api/calendar/semesters/{id}` - Delete semester
- `GET /api/calendar/semesters/{id}/weeks` - Get all weeks for a semester
- `POST /api/calendar/semesters/{id}/weeks` - Add a week to semester

**Schemas** (`backend/app/schemas/calendar.py`):
- Request/response validation using Pydantic
- Includes `CalendarSummary`, `Semester`, `SemesterWeek` schemas

### Frontend

**Calendar Sidebar Component** (`frontend/src/components/CalendarSidebar.tsx`):
- Displays current semester and week
- Shows upcoming holidays with red badges
- Shows upcoming exams with yellow badges
- Auto-refreshes every hour
- Responsive design with Tailwind CSS

**Integration**:
- Integrated into main sidebar (`frontend/src/components/Sidebar.tsx`)
- Appears at the top of the sidebar on all pages

## Setup Instructions

### 1. Run Database Migration

First, ensure PostgreSQL and Redis are running, then apply the database migration:

```bash
cd /home/laixin/projects/cms-whut/backend
source venv/bin/activate

# Run migration to create calendar tables
alembic upgrade head
```

This creates two tables:
- `semesters` - Semester information
- `semester_weeks` - Week-by-week breakdown

### 2. Initialize Sample Data

Run the initialization script to populate the database with 2025-2026 academic year data:

```bash
cd /home/laixin/projects/cms-whut/backend
source venv/bin/activate

# Initialize calendar data
python scripts/init_calendar_data.py
```

This will create:
- **2025-2026 First Semester** (Fall 2025)
  - September 1, 2025 - January 17, 2026
  - 20 weeks
  - National Day holiday (Week 5)
  - Exam weeks (Weeks 19-20)

- **2025-2026 Second Semester** (Spring 2026) - **Current**
  - February 23, 2026 - July 5, 2026
  - 19 weeks
  - Qingming Festival (Week 6)
  - Labor Day (Week 10)
  - Dragon Boat Festival (Week 15)
  - Exam weeks (Weeks 18-19)

### 3. Start Services

Start the backend and frontend:

```bash
# Terminal 1: Backend
cd /home/laixin/projects/cms-whut/backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd /home/laixin/projects/cms-whut/frontend
npm run dev
```

### 4. View the Calendar

Visit http://localhost:3000 and you should see the calendar sidebar on the right side showing:
- Current semester name
- Current week number (highlighted in blue)
- Upcoming holidays (if any)
- Upcoming exam weeks (if any)

## Adding Real Calendar Data

### Option 1: Manual Entry via API

You can create semesters and weeks using the API endpoints. Here's an example using curl:

```bash
# Create a new semester
curl -X POST http://localhost:8000/api/calendar/semesters \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2026-2027学年第一学期",
    "academic_year": "2026-2027",
    "semester_number": 1,
    "start_date": "2026-09-01",
    "end_date": "2027-01-17",
    "weeks": [
      {
        "week_number": 1,
        "start_date": "2026-09-01",
        "end_date": "2026-09-07",
        "notes": "开学第一周",
        "is_holiday": false,
        "is_exam_week": false
      }
    ]
  }'
```

### Option 2: Modify Initialization Script

Edit `backend/scripts/init_calendar_data.py` to add more semesters or update dates:

```python
def init_2026_2027_first_semester(db):
    semester = Semester(
        name="2026-2027学年第一学期",
        academic_year="2026-2027",
        semester_number=1,
        start_date=date(2026, 9, 1),
        end_date=date(2027, 1, 17),
        is_current=False
    )
    db.add(semester)
    db.flush()

    weeks = generate_weeks(date(2026, 9, 1), 20, semester.id)
    # Mark holidays, exams, etc.
    db.add_all(weeks)
```

### Option 3: Parse Calendar Images with OCR (Future)

For automated extraction from http://i.whut.edu.cn/xl, you could:

1. **Use PaddleOCR** (good for Chinese text):
```bash
pip install paddlepaddle paddleocr
```

2. **Create OCR script**:
```python
from paddleocr import PaddleOCR
import requests

# Download calendar image
image_url = "http://i.whut.edu.cn/xl/202512/W020251212562749789441.jpg"
response = requests.get(image_url)

# Run OCR
ocr = PaddleOCR(lang='ch')
result = ocr.ocr(image_url, cls=True)

# Parse results and populate database
# (This requires custom logic to parse the calendar format)
```

3. **Parse table structure** to extract:
   - Week numbers
   - Start/end dates
   - Holiday annotations
   - Exam week markers

## Database Schema

### Semesters Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| name | String(100) | Semester name (e.g., "2025-2026学年第一学期") |
| academic_year | String(20) | Academic year (e.g., "2025-2026") |
| semester_number | Integer | 1 or 2 (first or second semester) |
| start_date | Date | Semester start date |
| end_date | Date | Semester end date |
| is_current | Boolean | Only one semester should be current |
| calendar_image_url | String(500) | Optional: URL to calendar image |
| calendar_source_url | String(500) | Optional: Source page URL |
| created_at | Date | Creation timestamp |
| updated_at | Date | Update timestamp |

### Semester Weeks Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| semester_id | Integer | Foreign key to semesters |
| week_number | Integer | Week number (1, 2, 3, ...) |
| start_date | Date | Week start date (Monday) |
| end_date | Date | Week end date (Sunday) |
| notes | Text | Optional notes (e.g., "国庆节假期") |
| is_holiday | Boolean | Mark as holiday week |
| is_exam_week | Boolean | Mark as exam week |

## API Examples

### Get Calendar Summary

```bash
curl http://localhost:8000/api/calendar/summary
```

Response:
```json
{
  "current_semester": {
    "id": 2,
    "name": "2025-2026学年第二学期",
    "academic_year": "2025-2026",
    "semester_number": 2,
    "start_date": "2026-02-23",
    "end_date": "2026-07-05",
    "is_current": true,
    "is_active": true,
    "current_week": 5,
    "created_at": "2025-12-13"
  },
  "current_week": {
    "id": 25,
    "semester_id": 2,
    "week_number": 5,
    "start_date": "2026-03-23",
    "end_date": "2026-03-29",
    "notes": null,
    "is_holiday": false,
    "is_exam_week": false,
    "is_current": true
  },
  "upcoming_holidays": [
    {
      "id": 26,
      "week_number": 6,
      "start_date": "2026-03-30",
      "end_date": "2026-04-05",
      "notes": "清明节假期",
      "is_holiday": true,
      "is_exam_week": false
    }
  ],
  "upcoming_exams": []
}
```

### List All Semesters

```bash
curl http://localhost:8000/api/calendar/semesters
```

### Get Current Semester with All Weeks

```bash
curl http://localhost:8000/api/calendar/semesters/current
```

## Maintenance

### Update Current Semester

When a new semester starts, update the `is_current` flag:

```bash
# Set semester 3 as current
curl -X PATCH http://localhost:8000/api/calendar/semesters/3 \
  -H "Content-Type: application/json" \
  -d '{"is_current": true}'
```

This will automatically unset the previous current semester.

### Add a New Week

```bash
curl -X POST http://localhost:8000/api/calendar/semesters/2/weeks \
  -H "Content-Type: application/json" \
  -d '{
    "week_number": 20,
    "start_date": "2026-07-06",
    "end_date": "2026-07-12",
    "notes": "补课周",
    "is_holiday": false,
    "is_exam_week": false
  }'
```

## Future Enhancements

1. **Admin Interface**
   - Web UI to manage semesters and weeks
   - Calendar import from images using OCR
   - Bulk edit weeks

2. **Automated Updates**
   - Spider to check http://i.whut.edu.cn/xl for new calendar releases
   - OCR processing of calendar images
   - Automatic database population

3. **Additional Features**
   - Event reminders (email/push notifications)
   - Import/export to iCal format
   - Integration with course schedules
   - Week countdown widget

4. **Mobile Optimization**
   - Responsive calendar view
   - Swipe navigation between weeks
   - Add to home screen support

## Troubleshooting

### Calendar not showing

1. Check backend is running: `curl http://localhost:8000/api/calendar/summary`
2. Check database has data: `python scripts/init_calendar_data.py`
3. Check browser console for errors

### Database migration fails

```bash
# Check migration status
alembic current

# If stuck, try:
alembic downgrade -1
alembic upgrade head
```

### Sample data already exists

Run the init script again and choose "yes" when prompted to delete and recreate.

## Support

For issues or questions:
- Check API documentation: http://localhost:8000/docs
- Review backend logs
- Check frontend console for errors
- Refer to main project documentation in `/docs`
