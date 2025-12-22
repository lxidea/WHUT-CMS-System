#!/usr/bin/env python3
"""
OCR-based Calendar Extractor for WHUT Calendar Images

This module uses PaddleOCR to extract text from WHUT semester calendar images
and parse them into structured data for database insertion.

Usage:
    from ocr_calendar_extractor import extract_calendar_from_url

    calendar_data = extract_calendar_from_url(
        "http://i.whut.edu.cn/xl/202512/W020251212562749789441.jpg"
    )
"""

import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from io import BytesIO
import cv2
import numpy as np
from paddleocr import PaddleOCR
from bs4 import BeautifulSoup


class CalendarOCRExtractor:
    """Extract semester calendar data from images using OCR"""

    def __init__(self, use_gpu=False):
        """Initialize PaddleOCR"""
        # PaddleOCR 3.x simplified API
        self.ocr = PaddleOCR(lang='ch')

    def download_image(self, url: str) -> np.ndarray:
        """Download image from URL and convert to numpy array"""
        print(f"📥 Downloading image from: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Convert to numpy array
        image = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        print(f"✓ Image downloaded: {image.shape}")
        return image

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to get better contrast
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

        return denoised

    def extract_text_from_image(self, image: np.ndarray) -> List[Tuple[str, float]]:
        """Extract text from image using OCR"""
        print("🔍 Running OCR on image...")

        # Resize large images for faster processing
        height, width = image.shape[:2]
        max_dimension = 2000  # Maximum width or height

        if height > max_dimension or width > max_dimension:
            scale = min(max_dimension / height, max_dimension / width)
            new_height = int(height * scale)
            new_width = int(width * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"  Resized to {new_width}x{new_height} for faster processing")

        # Run OCR directly on image (PaddleOCR handles preprocessing)
        result = self.ocr.predict(image)

        # Extract text and confidence
        texts = []

        # Debug: Print result structure
        print(f"  Debug: result type = {type(result)}")
        if isinstance(result, list) and len(result) > 0:
            print(f"  Debug: first item type = {type(result[0])}")
            if isinstance(result[0], dict):
                print(f"  Debug: keys = {list(result[0].keys())}")

        # PaddleOCR 3.x returns a list of OCRResult objects
        if isinstance(result, list):
            for page_result in result:
                # Handle both dict and object formats
                if hasattr(page_result, 'rec_texts') and hasattr(page_result, 'rec_scores'):
                    # Object format (OCRResult)
                    for text, score in zip(page_result.rec_texts, page_result.rec_scores):
                        texts.append((text, score))
                elif isinstance(page_result, dict):
                    # Dict format with rec_texts and rec_scores (plural)
                    if 'rec_texts' in page_result and 'rec_scores' in page_result:
                        for text, score in zip(page_result['rec_texts'], page_result['rec_scores']):
                            texts.append((text, score))
                    elif 'text' in page_result:
                        texts.append((page_result['text'], page_result.get('score', 1.0)))

        print(f"✓ Extracted {len(texts)} text blocks")

        # Debug: Show extracted text to understand format
        if texts:
            print("\n📝 Sample extracted text (first 100 blocks):")
            print("=" * 70)
            for i, (text, conf) in enumerate(texts[:100], 1):
                print(f"{i:3d}. [{conf:.3f}] {text}")
            print("=" * 70)

            # Also search for week-related text
            print("\n🔍 Searching for week-related patterns:")
            print("=" * 70)
            week_related = []
            for text, conf in texts:
                # Look for week numbers, dates, or month patterns
                if any(keyword in text for keyword in ['周', '第', '月', '日', '节', '假', '考']):
                    week_related.append((text, conf))

            print(f"Found {len(week_related)} week/date-related text blocks")
            for i, (text, conf) in enumerate(week_related[:30], 1):
                print(f"  {i:2d}. [{conf:.3f}] {text}")
            print("=" * 70)

        return texts

    def parse_semester_info(self, texts: List[Tuple[str, float]]) -> Dict:
        """Parse semester information from OCR text"""
        semester_info = {
            'name': None,
            'academic_year': None,
            'semester_number': None,
            'start_date': None,
            'end_date': None
        }

        # Combine all text for easier parsing
        full_text = ' '.join([t[0] for t in texts])

        # Extract academic year (e.g., "2025-2026")
        year_match = re.search(r'(\d{4})[—\-~～](\d{4})', full_text)
        if year_match:
            semester_info['academic_year'] = f"{year_match.group(1)}-{year_match.group(2)}"

        # Extract semester number (第一学期 or 第二学期)
        if '第一学期' in full_text or '第1学期' in full_text:
            semester_info['semester_number'] = 1
            semester_info['name'] = f"{semester_info['academic_year']}学年第一学期"
        elif '第二学期' in full_text or '第2学期' in full_text:
            semester_info['semester_number'] = 2
            semester_info['name'] = f"{semester_info['academic_year']}学年第二学期"

        print(f"📅 Detected semester: {semester_info['name']}")
        return semester_info

    def parse_week_data(self, texts: List[Tuple[str, float]], semester_info: Dict) -> List[Dict]:
        """Parse week data from OCR text"""
        weeks = []

        # New approach: Look for semester duration text like "本学期共19个教学周，2026年3月2日至2026年7月12日止"
        # The text might be split across OCR blocks, so join with no spaces and also with spaces
        full_text_nospace = ''.join([t[0] for t in texts])
        full_text = ' '.join([t[0] for t in texts])

        # Try both versions
        duration_pattern = re.compile(r'本学期共(\d+)个教学周.*?(\d{4})年(\d{1,2})月(\d{1,2})日至.*?(\d{4})年(\d{1,2})月(\d{1,2})日')

        duration_match = duration_pattern.search(full_text_nospace)
        if not duration_match:
            duration_match = duration_pattern.search(full_text)
        if duration_match:
            num_weeks = int(duration_match.group(1))
            start_year = int(duration_match.group(2))
            start_month = int(duration_match.group(3))
            start_day = int(duration_match.group(4))
            end_year = int(duration_match.group(5))
            end_month = int(duration_match.group(6))
            end_day = int(duration_match.group(7))

            try:
                start_date = datetime(start_year, start_month, start_day).date()
                end_date = datetime(end_year, end_month, end_day).date()

                print(f"  Found duration: {num_weeks} weeks from {start_date} to {end_date}")

                # Update semester info
                semester_info['start_date'] = start_date
                semester_info['end_date'] = end_date

                # Generate weeks
                current_date = start_date
                for week_num in range(1, num_weeks + 1):
                    week_end = current_date + timedelta(days=6)

                    week_data = {
                        'week_number': week_num,
                        'start_date': current_date,
                        'end_date': week_end,
                        'notes': None,
                        'is_holiday': False,
                        'is_exam_week': False
                    }
                    weeks.append(week_data)
                    current_date = week_end + timedelta(days=1)

            except ValueError as e:
                print(f"⚠️  Invalid date: {e}")

        # Find holidays and mark them
        holidays = {
            '元宵节': '元宵节',
            '清明': '清明节假期',
            '劳动节': '劳动节假期',
            '端午节': '端午节假期',
            '中秋': '中秋节假期',
            '国庆': '国庆节假期',
            '七夕': '七夕节'
        }

        for keyword, holiday_name in holidays.items():
            if keyword in full_text:
                print(f"  Found holiday: {holiday_name}")
                # You could try to determine which week it falls in

        # Look for exam mentions
        if '考试' in full_text or '期末' in full_text:
            print(f"  Found exam period mentioned")
            # Mark last 2 weeks as exam weeks
            if len(weeks) >= 2:
                weeks[-2]['is_exam_week'] = True
                weeks[-2]['notes'] = '期末考试周'
                weeks[-1]['is_exam_week'] = True
                weeks[-1]['notes'] = '期末考试周'

        print(f"✓ Generated {len(weeks)} weeks")
        return weeks

    def _extract_holiday_name(self, text: str) -> str:
        """Extract holiday name from text"""
        # Common holiday patterns
        holidays = {
            '国庆': '国庆节假期',
            '清明': '清明节假期',
            '端午': '端午节假期',
            '劳动': '劳动节假期',
            '春节': '春节假期',
            '中秋': '中秋节假期',
            '元旦': '元旦假期'
        }

        for key, value in holidays.items():
            if key in text:
                return value

        return '假期'

    def _fill_missing_weeks(self, weeks: List[Dict]) -> List[Dict]:
        """Fill in missing weeks by interpolation"""
        if not weeks:
            return weeks

        filled_weeks = []
        for i, week in enumerate(weeks):
            filled_weeks.append(week)

            # Check if there's a gap to the next week
            if i < len(weeks) - 1:
                current_week_num = week['week_number']
                next_week_num = weeks[i + 1]['week_number']

                if next_week_num - current_week_num > 1:
                    # Fill the gap
                    for gap_week_num in range(current_week_num + 1, next_week_num):
                        # Calculate dates based on 7-day increments
                        days_offset = (gap_week_num - current_week_num) * 7
                        gap_start = week['start_date'] + timedelta(days=days_offset)
                        gap_end = gap_start + timedelta(days=6)

                        gap_week = {
                            'week_number': gap_week_num,
                            'start_date': gap_start,
                            'end_date': gap_end,
                            'notes': None,
                            'is_holiday': False,
                            'is_exam_week': False
                        }
                        filled_weeks.append(gap_week)

        # Re-sort
        filled_weeks.sort(key=lambda x: x['week_number'])
        return filled_weeks

    def extract_calendar_from_image(self, image: np.ndarray) -> Dict:
        """Main extraction pipeline"""
        # Extract text
        texts = self.extract_text_from_image(image)

        # Parse semester info
        semester_info = self.parse_semester_info(texts)

        # Parse weeks
        weeks = self.parse_week_data(texts, semester_info)

        # Calculate start and end dates from weeks
        if weeks:
            semester_info['start_date'] = weeks[0]['start_date']
            semester_info['end_date'] = weeks[-1]['end_date']

        return {
            'semester': semester_info,
            'weeks': weeks
        }

    def extract_calendar_from_url(self, url: str) -> Dict:
        """Extract calendar from image URL"""
        image = self.download_image(url)
        return self.extract_calendar_from_image(image)


# Convenience function
def extract_calendar_from_url(url: str, use_gpu: bool = False) -> Dict:
    """Extract calendar data from image URL"""
    extractor = CalendarOCRExtractor(use_gpu=use_gpu)
    return extractor.extract_calendar_from_url(url)


def fetch_calendar_page_images() -> List[Dict]:
    """Fetch all calendar image URLs from http://i.whut.edu.cn/xl"""
    print("📋 Fetching calendar list from http://i.whut.edu.cn/xl/")

    response = requests.get("http://i.whut.edu.cn/xl/", timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')

    calendars = []
    # Find all calendar links
    links = soup.select('ul.normal_list2 li a')

    for link in links[:5]:  # Get latest 5 calendars
        title = link.get('title', '')
        href = link.get('href', '')

        if href and title:
            # Construct full URL
            if not href.startswith('http'):
                href = f"http://i.whut.edu.cn/xl/{href}"

            calendars.append({
                'title': title,
                'detail_url': href
            })

    print(f"✓ Found {len(calendars)} calendar entries")
    return calendars


def fetch_calendar_image_url(detail_url: str) -> Optional[str]:
    """Fetch calendar image URL from detail page"""
    print(f"🔗 Fetching calendar image from: {detail_url}")

    response = requests.get(detail_url, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find image in content
    img = soup.select_one('div.TRS_Editor img')
    if img:
        img_src = img.get('src', '')
        if img_src:
            # Construct full URL
            if not img_src.startswith('http'):
                base_url = '/'.join(detail_url.split('/')[:-1])
                img_src = f"{base_url}/{img_src}"

            print(f"✓ Found image: {img_src}")
            return img_src

    print("⚠️  No image found on page")
    return None


if __name__ == "__main__":
    # Test extraction
    print("\n" + "=" * 60)
    print("WHUT Calendar OCR Extractor - Test Mode")
    print("=" * 60 + "\n")

    # Example: Extract from a specific URL
    test_url = "http://i.whut.edu.cn/xl/202512/W020251212562749789441.jpg"

    try:
        result = extract_calendar_from_url(test_url)

        print("\n" + "=" * 60)
        print("Extraction Results:")
        print("=" * 60)
        print(f"\nSemester: {result['semester']['name']}")
        print(f"Academic Year: {result['semester']['academic_year']}")
        print(f"Start Date: {result['semester']['start_date']}")
        print(f"End Date: {result['semester']['end_date']}")
        print(f"\nWeeks extracted: {len(result['weeks'])}")

        if result['weeks']:
            print("\nSample weeks:")
            for week in result['weeks'][:5]:
                holiday = " [假期]" if week['is_holiday'] else ""
                exam = " [考试]" if week['is_exam_week'] else ""
                notes = f" - {week['notes']}" if week['notes'] else ""
                print(f"  第{week['week_number']}周: {week['start_date']} - {week['end_date']}{holiday}{exam}{notes}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
