# Calendar Feature - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- PostgreSQL running
- Backend virtual environment activated

### Step 1: Install OCR Dependencies (2 min)

```bash
cd /home/laixin/projects/cms-whut/backend
source venv/bin/activate
pip install -r requirements.txt
```

This installs PaddleOCR and other OCR dependencies.

### Step 2: Run Database Migration (30 sec)

```bash
# Create calendar tables
alembic upgrade head
```

### Step 3: Import Calendars Automatically (2 min)

```bash
# Option A: Import latest calendar only (recommended for first time)
python scripts/auto_import_calendar.py --latest-only

# Option B: Import all available calendars
python scripts/auto_import_calendar.py

# Option C: Preview before importing (dry run)
python scripts/auto_import_calendar.py --latest-only --dry-run
```

**What this does:**
1. Fetches calendar pages from http://i.whut.edu.cn/xl
2. Downloads calendar images
3. Extracts text using Chinese OCR (PaddleOCR)
4. Parses semester info, weeks, holidays, exams
5. Populates database automatically

### Step 4: Set Current Semester (10 sec)

```bash
# Start backend if not running
uvicorn app.main:app --reload
```

In another terminal:
```bash
# List semesters to find the ID
curl http://localhost:8000/api/calendar/semesters

# Set the current semester (replace ID with the correct one)
curl -X PATCH http://localhost:8000/api/calendar/semesters/1 \
  -H "Content-Type: application/json" \
  -d '{"is_current": true}'
```

### Step 5: View Calendar in Frontend (30 sec)

```bash
# In another terminal, start frontend
cd /home/laixin/projects/cms-whut/frontend
npm run dev
```

Visit http://localhost:3000 - you'll see the calendar sidebar showing:
- ✅ Current semester name
- ✅ Current week number (blue badge)
- ✅ Upcoming holidays (red badges)
- ✅ Upcoming exam weeks (yellow badges)

---

## 📊 What You Get

### Calendar Sidebar Display

```
┌─────────────────────────────────┐
│ 📅 学期校历                      │
├─────────────────────────────────┤
│ 当前学期                         │
│ 2025-2026学年第二学期            │
│ 2025-2026 学年 第2学期           │
├─────────────────────────────────┤
│ 本周                 [第 5 周]   │
│ 3月23日 - 3月29日                │
├─────────────────────────────────┤
│ 🔔 即将到来的假期                │
│ ┌───────────────────────────┐   │
│ │ 第 6 周      3月30日       │   │
│ │ 清明节假期                 │   │
│ └───────────────────────────┘   │
├─────────────────────────────────┤
│ 📝 即将到来的考试                │
│ ┌───────────────────────────┐   │
│ │ 第 18 周     6月14日      │   │
│ │ 期末考试周                 │   │
│ └───────────────────────────┘   │
└─────────────────────────────────┘
```

### Automatic Data Extraction

The OCR system automatically detects:
- ✅ Academic year (e.g., "2025-2026")
- ✅ Semester number (1 or 2)
- ✅ Week numbers (1-20)
- ✅ Date ranges for each week
- ✅ Holidays (国庆节, 清明节, 劳动节, 端午节, etc.)
- ✅ Exam weeks (期末考试周)

---

## 🔧 Maintenance

### Update Calendar Periodically

Run this when new calendars are published:

```bash
cd /home/laixin/projects/cms-whut/backend
source venv/bin/activate
python scripts/auto_import_calendar.py --latest-only
```

### Manual Data Entry (Alternative)

If OCR doesn't work well, use the manual script:

```bash
python scripts/init_calendar_data.py
```

Then edit the script to add your data.

---

## 📚 Documentation

- **Full setup guide**: `docs/CALENDAR_FEATURE.md`
- **OCR details**: `docs/OCR_CALENDAR_IMPORT.md`
- **API reference**: http://localhost:8000/docs (when backend running)

---

## ❓ Troubleshooting

### OCR Dependencies Won't Install

Try installing with mirrors:
```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
pip install paddleocr opencv-python
```

### No Text Extracted

The image quality might be too low. Try:
1. Download the image manually and check quality
2. Adjust threshold in `ocr_calendar_extractor.py` (line ~60):
   ```python
   _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # Lower value
   ```

### Calendar Not Showing in Frontend

1. Check backend is running: `curl http://localhost:8000/api/calendar/summary`
2. Check database has data: `curl http://localhost:8000/api/calendar/semesters`
3. Make sure a semester is marked as `is_current: true`

### Database Migration Fails

Database not running:
```bash
# Check if PostgreSQL is running
sudo service postgresql status

# Start it if needed
sudo service postgresql start
```

---

## 🎯 Next Steps

1. **Set up automation**: Add calendar import to Celery tasks for weekly updates
2. **Customize appearance**: Edit `CalendarSidebar.tsx` to match your design
3. **Add features**: Exam countdowns, email reminders, etc.

---

**That's it!** You now have an automated calendar system that:
- 🤖 Automatically extracts data from WHUT calendar images
- 📅 Displays current week in the sidebar
- 🔔 Shows upcoming holidays and exams
- 🔄 Easy to update when new calendars are published

Enjoy your new calendar feature! 🎉
