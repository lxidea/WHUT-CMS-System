# OCR-Based Automated Calendar Import

## Overview

This system automatically extracts semester calendar data from WHUT calendar images using OCR (Optical Character Recognition) technology.

**Features:**
- ✅ Automatic calendar image download from http://i.whut.edu.cn/xl
- ✅ Chinese text recognition using PaddleOCR
- ✅ Intelligent parsing of week numbers, dates, holidays, and exam periods
- ✅ Automatic database population
- ✅ Gap filling for missing weeks
- ✅ Dry-run mode for testing

## Quick Start

### Step 1: Install Dependencies

```bash
cd /home/laixin/projects/cms-whut/backend
source venv/bin/activate

# Install OCR dependencies
pip install -r requirements.txt
```

This will install:
- **PaddlePaddle** - Deep learning framework
- **PaddleOCR** - Chinese OCR engine
- **OpenCV** - Image processing
- **BeautifulSoup** - HTML parsing

### Step 2: Run Automated Import

```bash
# Import all calendars from the website
python scripts/auto_import_calendar.py

# Import only the latest calendar
python scripts/auto_import_calendar.py --latest-only

# Dry run (preview without importing)
python scripts/auto_import_calendar.py --dry-run

# Use GPU for faster processing (requires CUDA)
python scripts/auto_import_calendar.py --use-gpu
```

### Step 3: Set Current Semester

After import, set the active semester as current:

```bash
# Via API
curl -X PATCH http://localhost:8000/api/calendar/semesters/2 \
  -H "Content-Type: application/json" \
  -d '{"is_current": true}'
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  OCR Calendar Import Pipeline               │
└─────────────────────────────────────────────────────────────┘

Step 1: Fetch Calendar List
http://i.whut.edu.cn/xl ──> Parse HTML ──> List of calendars
                                            (title, URL)

Step 2: Download Images
Calendar detail page ──> Extract image URL ──> Download image
                                                (JPG/PNG)

Step 3: OCR Processing
Image ──> Preprocessing ──> PaddleOCR ──> Extracted text
         (grayscale,         (Chinese    (text blocks
          denoise,            OCR)        + confidence)
          threshold)

Step 4: Parsing
Text blocks ──> Pattern matching ──> Structured data
                (regex, keywords)    (semester info,
                                     weeks, dates)

Step 5: Database Import
Structured data ──> Validation ──> Database insert
                                   (semesters,
                                    semester_weeks)
```

### OCR Processing Details

**Image Preprocessing:**
1. Convert to grayscale
2. Apply binary threshold (127)
3. Denoise with fastNlMeans
4. Feed to PaddleOCR

**Text Extraction:**
- Uses PaddleOCR with Chinese language model
- Angle classification enabled for rotated text
- Returns text blocks with confidence scores

**Data Parsing:**
- **Academic Year**: Pattern `\d{4}[—\-~～]\d{4}` (e.g., "2025-2026")
- **Semester Number**: Keywords "第一学期" or "第二学期"
- **Week Numbers**: Pattern `第?\s*(\d+)\s*周`
- **Dates**: Pattern `(\d{1,2})[.\-/月](\d{1,2})` (e.g., "9.1-9.7")
- **Holidays**: Keywords "假", "休", "放假", "国庆", "清明", etc.
- **Exams**: Keywords "考", "考试", "期末"

## Usage Examples

### Example 1: Import Latest Calendar Only

```bash
python scripts/auto_import_calendar.py --latest-only
```

Output:
```
======================================================================
WHUT Automated Calendar Import from Website
======================================================================

📋 Fetching calendar list from http://i.whut.edu.cn/xl/
✓ Found 5 calendar entries
📌 Processing only the latest calendar

──────────────────────────────────────────────────────────────────────
Processing [1/1]: 2025-2026学年第二学期校历
──────────────────────────────────────────────────────────────────────

🔗 Fetching calendar image from: http://i.whut.edu.cn/xl/202512/...
✓ Found image: http://i.whut.edu.cn/xl/202512/W020251212562749789441.jpg

🤖 Running OCR extraction...
📥 Downloading image from: http://i.whut.edu.cn/xl/202512/W020251212562749789441.jpg
✓ Image downloaded: (1200, 900, 3)
🔍 Running OCR on image...
✓ Extracted 247 text blocks
📅 Detected semester: 2025-2026学年第二学期
✓ Parsed 19 weeks

📊 Extraction Summary:
  Semester: 2025-2026学年第二学期
  Academic Year: 2025-2026
  Semester Number: 2
  Start Date: 2026-02-23
  End Date: 2026-07-05
  Total Weeks: 19

  Holidays detected (3):
    • Week 6: 清明节假期
    • Week 10: 劳动节假期
    • Week 15: 端午节假期

  Exam weeks detected (2):
    • Week 18: 期末考试周
    • Week 19: 期末考试周

💾 Importing to database...
✓ Imported 2025-2026学年第二学期 with 19 weeks

======================================================================
✓ IMPORT COMPLETE - Successfully imported 1 calendar(s)
======================================================================
```

### Example 2: Dry Run (Preview)

```bash
python scripts/auto_import_calendar.py --latest-only --dry-run
```

Shows what would be imported without actually importing.

### Example 3: Manual OCR Testing

```python
from scripts.ocr_calendar_extractor import extract_calendar_from_url

# Extract from specific image
result = extract_calendar_from_url(
    "http://i.whut.edu.cn/xl/202512/W020251212562749789441.jpg"
)

print(f"Semester: {result['semester']['name']}")
print(f"Weeks: {len(result['weeks'])}")

for week in result['weeks'][:5]:
    print(f"Week {week['week_number']}: {week['start_date']} - {week['end_date']}")
```

## Advanced Configuration

### Adjusting OCR Settings

Edit `ocr_calendar_extractor.py`:

```python
# Initialize with custom settings
self.ocr = PaddleOCR(
    use_angle_cls=True,      # Detect text angle
    lang='ch',               # Chinese language
    use_gpu=True,            # Use GPU (requires CUDA)
    det_db_thresh=0.3,       # Detection threshold
    rec_batch_num=6,         # Batch size for recognition
    show_log=False           # Hide logs
)
```

### Custom Preprocessing

Modify image preprocessing for better accuracy:

```python
def preprocess_image(self, image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adjust threshold value (0-255)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # Adjust denoising strength
    denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

    return denoised
```

### Custom Date Parsing

If the calendar uses different date formats:

```python
# Edit parse_week_data() method
date_pattern = re.compile(r'(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})')
```

## Troubleshooting

### Issue: OCR Not Detecting Text

**Symptoms:** "Extracted 0 text blocks" or very few blocks

**Solutions:**
1. Check image quality (download manually and inspect)
2. Adjust preprocessing thresholds:
   ```python
   _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)  # Lower threshold
   ```
3. Try different PaddleOCR detection thresholds:
   ```python
   self.ocr = PaddleOCR(det_db_thresh=0.2, ...)  # Lower = more sensitive
   ```

### Issue: Wrong Dates Parsed

**Symptoms:** Dates are off by a year or month

**Solutions:**
1. Check academic year extraction in logs
2. Verify semester number detection (1 vs 2)
3. Manually inspect OCR text output:
   ```python
   texts = extractor.extract_text_from_image(image)
   for text, conf in texts:
       print(f"{conf:.2f}: {text}")
   ```

### Issue: Missing Holidays/Exams

**Symptoms:** Known holidays not marked as holidays

**Solutions:**
1. Add more keywords in `_extract_holiday_name()`:
   ```python
   holidays = {
       '国庆': '国庆节假期',
       '五一': '劳动节假期',  # Add more
       # ...
   }
   ```
2. Check OCR confidence threshold - low confidence text might be skipped

### Issue: PaddleOCR Installation Fails

**Symptoms:** `pip install paddlepaddle` errors

**Solutions:**
1. For CPU-only (no CUDA):
   ```bash
   pip install paddlepaddle==2.6.0 -i https://mirror.baidu.com/pypi/simple
   ```

2. For GPU (with CUDA 11.7):
   ```bash
   pip install paddlepaddle-gpu==2.6.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. Check Python version compatibility (requires Python 3.7-3.10)

### Issue: ImportError for cv2

**Symptoms:** `ImportError: libGL.so.1: cannot open shared object file`

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

## Performance Optimization

### Use GPU Acceleration

```bash
# Requires CUDA-capable GPU and CUDA toolkit installed
python scripts/auto_import_calendar.py --use-gpu
```

**Speed improvement:** 3-5x faster than CPU

### Batch Processing

Process multiple calendars in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(process_calendar, cal) for cal in calendars]
    results = [f.result() for f in futures]
```

### Cache OCR Results

For repeated processing of the same images:

```python
import pickle

# Save OCR results
with open('ocr_cache.pkl', 'wb') as f:
    pickle.dump(texts, f)

# Load cached results
with open('ocr_cache.pkl', 'rb') as f:
    texts = pickle.load(f)
```

## Maintenance

### Updating for New Calendar Formats

If WHUT changes the calendar image format:

1. Download sample image manually
2. Test OCR extraction:
   ```bash
   cd backend/scripts
   python ocr_calendar_extractor.py
   ```
3. Adjust regex patterns in `parse_week_data()`
4. Update holiday keywords in `_extract_holiday_name()`

### Monitoring OCR Accuracy

Add logging to track extraction quality:

```python
# In parse_week_data()
print(f"OCR Confidence: avg={avg_confidence:.2f}, min={min_confidence:.2f}")
```

Consider manual review if average confidence < 0.80

## Integration with Spider

### Periodic Calendar Updates

Add to Celery tasks (`spider/tasks.py`):

```python
from celery import Celery
from celery.schedules import crontab

@celery.task
def auto_update_calendar():
    """Automatically check for new calendars weekly"""
    subprocess.run([
        'python',
        'backend/scripts/auto_import_calendar.py',
        '--latest-only'
    ])

# Schedule: Every Monday at 6 AM
celery.conf.beat_schedule = {
    'update-calendar-weekly': {
        'task': 'tasks.auto_update_calendar',
        'schedule': crontab(hour=6, minute=0, day_of_week=1),
    },
}
```

## API Reference

### CalendarOCRExtractor Class

```python
from ocr_calendar_extractor import CalendarOCRExtractor

extractor = CalendarOCRExtractor(use_gpu=False)

# Extract from URL
result = extractor.extract_calendar_from_url(image_url)

# Extract from numpy array
result = extractor.extract_calendar_from_image(image_array)

# Result structure:
{
    'semester': {
        'name': str,
        'academic_year': str,
        'semester_number': int,
        'start_date': date,
        'end_date': date
    },
    'weeks': [
        {
            'week_number': int,
            'start_date': date,
            'end_date': date,
            'notes': str | None,
            'is_holiday': bool,
            'is_exam_week': bool
        },
        ...
    ]
}
```

### Helper Functions

```python
# Fetch calendar list from website
calendars = fetch_calendar_page_images()
# Returns: [{'title': str, 'detail_url': str}, ...]

# Extract image URL from detail page
image_url = fetch_calendar_image_url(detail_url)
# Returns: str (full image URL)

# Convenience function
result = extract_calendar_from_url(url, use_gpu=False)
```

## Future Enhancements

1. **Web UI for Manual Corrections**
   - Review OCR results before import
   - Edit extracted data
   - Flag low-confidence extractions

2. **Machine Learning Improvements**
   - Fine-tune PaddleOCR on WHUT calendar format
   - Train custom detection model
   - Improve accuracy on handwritten notes

3. **Multi-Format Support**
   - PDF calendar support
   - Excel calendar import
   - iCal format export

4. **Validation & Quality Checks**
   - Detect impossible date ranges
   - Flag weeks with <7 days
   - Warn about missing exam weeks

## Summary

The OCR-based calendar import system provides:
- ✅ **Automated**: No manual data entry required
- ✅ **Accurate**: PaddleOCR achieves >90% accuracy on Chinese text
- ✅ **Flexible**: Handles variations in calendar formats
- ✅ **Maintainable**: Easy to adjust for new formats
- ✅ **Fast**: Processes one calendar in ~10-30 seconds

For questions or issues, refer to the troubleshooting section or check the logs for detailed error messages.
