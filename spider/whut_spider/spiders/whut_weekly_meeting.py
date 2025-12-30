import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape
import json


class WhutWeeklyMeetingSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology Weekly Meeting Schedule
    (https://ioa.whut.edu.cn/seeyon/ext/NewWeekMeeting.do?method=pubIndex)

    This spider extracts weekly meeting schedules from the university's
    internal OA system. The meeting schedule typically includes:
    - Meeting time (会议时间)
    - Meeting location (会议地点)
    - Meeting topic/content (会议内容)
    - Organizer/Host department (主办单位)
    - Participants (参加人员)

    Note: This spider requires access to the university internal network (VPN).
    """
    name = 'whut_weekly_meeting'
    allowed_domains = ['ioa.whut.edu.cn']

    start_urls = [
        'https://ioa.whut.edu.cn/seeyon/ext/NewWeekMeeting.do?method=pubIndex',
    ]

    # Track visited URLs
    visited_urls = set()

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'ROBOTSTXT_OBEY': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }

    def parse(self, response):
        """
        Parse the weekly meeting schedule page
        """
        self.logger.info(f'Parsing Weekly Meeting page: {response.url}')

        # Try to determine page structure
        # Strategy 1: Table-based layout (most common for meeting schedules)
        tables = response.css('table')
        if tables:
            yield from self.parse_table_layout(response, tables)
            return

        # Strategy 2: List-based layout
        meeting_items = response.css(
            'div.meeting-item, '
            'div.schedule-item, '
            'li.meeting, '
            'div.item'
        )
        if meeting_items:
            yield from self.parse_list_layout(response, meeting_items)
            return

        # Strategy 3: JSON API response (some Seeyon systems use AJAX)
        if response.headers.get('Content-Type', b'').startswith(b'application/json'):
            yield from self.parse_json_response(response)
            return

        # Strategy 4: Generic extraction
        yield from self.parse_generic(response)

    def parse_table_layout(self, response, tables):
        """
        Parse table-based meeting schedule
        """
        for table in tables:
            rows = table.css('tr')

            # Skip empty tables
            if len(rows) < 2:
                continue

            # Try to identify header row
            header_row = rows[0]
            headers = header_row.css('th::text, td::text').getall()
            headers = [h.strip() for h in headers if h.strip()]

            # Map column indices
            col_map = {}
            for i, header in enumerate(headers):
                if any(k in header for k in ['时间', '日期']):
                    col_map['time'] = i
                elif any(k in header for k in ['地点', '地址', '会场']):
                    col_map['location'] = i
                elif any(k in header for k in ['内容', '议题', '主题', '会议名称']):
                    col_map['topic'] = i
                elif any(k in header for k in ['主办', '部门', '单位']):
                    col_map['organizer'] = i
                elif any(k in header for k in ['参加', '出席', '人员']):
                    col_map['participants'] = i

            # Process data rows
            for row in rows[1:]:
                cells = row.css('td')
                if not cells:
                    continue

                # Extract meeting info
                meeting_info = self.extract_meeting_from_row(cells, col_map)
                if meeting_info.get('topic'):
                    yield from self.create_meeting_item(response, meeting_info)

    def extract_meeting_from_row(self, cells, col_map):
        """
        Extract meeting information from a table row
        """
        meeting_info = {}

        for key, idx in col_map.items():
            if idx < len(cells):
                text = cells[idx].css('::text').get()
                if text:
                    meeting_info[key] = text.strip()

        # If no column mapping, try to extract intelligently
        if not col_map:
            all_texts = [c.css('::text').get() for c in cells]
            all_texts = [t.strip() for t in all_texts if t and t.strip()]

            for text in all_texts:
                # Time pattern
                if re.match(r'\d{1,2}[:\：]\d{2}', text) or '时' in text:
                    meeting_info['time'] = text
                # Location pattern (contains room/hall/building)
                elif any(loc in text for loc in ['楼', '室', '厅', '会议', '馆']):
                    meeting_info['location'] = text
                # Longer text is likely the topic
                elif len(text) > 10 and 'topic' not in meeting_info:
                    meeting_info['topic'] = text

        return meeting_info

    def parse_list_layout(self, response, items):
        """
        Parse list-based meeting schedule
        """
        for item in items:
            meeting_info = {}

            # Extract time
            time_elem = item.css('.time::text, .date::text, span.time::text').get()
            if time_elem:
                meeting_info['time'] = time_elem.strip()

            # Extract location
            location_elem = item.css('.location::text, .place::text, span.location::text').get()
            if location_elem:
                meeting_info['location'] = location_elem.strip()

            # Extract topic/title
            topic_elem = item.css('.title::text, .topic::text, h3::text, h4::text, a::text').get()
            if topic_elem:
                meeting_info['topic'] = topic_elem.strip()

            # Extract organizer
            org_elem = item.css('.organizer::text, .dept::text').get()
            if org_elem:
                meeting_info['organizer'] = org_elem.strip()

            if meeting_info.get('topic'):
                yield from self.create_meeting_item(response, meeting_info)

    def parse_json_response(self, response):
        """
        Parse JSON API response
        """
        try:
            data = json.loads(response.text)

            # Handle various JSON structures
            meetings = []
            if isinstance(data, list):
                meetings = data
            elif isinstance(data, dict):
                meetings = data.get('data', data.get('items', data.get('meetings', [])))

            for meeting in meetings:
                meeting_info = {
                    'topic': meeting.get('title') or meeting.get('topic') or meeting.get('subject'),
                    'time': meeting.get('time') or meeting.get('startTime') or meeting.get('meetingTime'),
                    'location': meeting.get('location') or meeting.get('place') or meeting.get('room'),
                    'organizer': meeting.get('organizer') or meeting.get('department') or meeting.get('host'),
                    'participants': meeting.get('participants') or meeting.get('attendees'),
                }

                if meeting_info.get('topic'):
                    yield from self.create_meeting_item(response, meeting_info)

        except json.JSONDecodeError as e:
            self.logger.warning(f'Failed to parse JSON: {e}')

    def parse_generic(self, response):
        """
        Generic fallback parser
        """
        # Extract week information
        week_info = response.css('h1::text, h2::text, div.title::text').get()

        # Look for meeting-related content blocks
        content_blocks = response.css('div.content, div.main, div.body')

        for block in content_blocks:
            text = block.get()
            if not text:
                continue

            # Look for meeting patterns in text
            meetings = self.extract_meetings_from_text(text)
            for meeting_info in meetings:
                if week_info:
                    meeting_info['week'] = week_info.strip()
                yield from self.create_meeting_item(response, meeting_info)

    def extract_meetings_from_text(self, text):
        """
        Extract meeting information from unstructured text
        """
        meetings = []

        # Clean HTML
        text = re.sub(r'<[^>]+>', '\n', text)
        text = unescape(text)

        # Split by common meeting separators
        sections = re.split(r'\n\s*\n|\d+[、.]', text)

        for section in sections:
            section = section.strip()
            if len(section) < 10:
                continue

            meeting = {}

            # Extract time
            time_match = re.search(
                r'(\d{1,2}月\d{1,2}日|\d{1,2}[:\：]\d{2}|周[一二三四五六日]|星期[一二三四五六日天])',
                section
            )
            if time_match:
                meeting['time'] = time_match.group(1)

            # Extract location
            loc_match = re.search(
                r'(地点|地址)[：:]\s*([^\n\r]+)|'
                r'在([^\n\r]*?(?:楼|室|厅|馆|中心)[^\n\r]*)',
                section
            )
            if loc_match:
                meeting['location'] = loc_match.group(2) or loc_match.group(3)

            # The remaining text is likely the topic
            if meeting.get('time') or meeting.get('location'):
                topic = re.sub(r'地点[：:][^\n]+', '', section)
                topic = re.sub(r'\d{1,2}[:\：]\d{2}', '', topic)
                topic = topic.strip()
                if len(topic) > 5:
                    meeting['topic'] = topic[:200]

            if meeting.get('topic'):
                meetings.append(meeting)

        return meetings

    def create_meeting_item(self, response, meeting_info):
        """
        Create a NewsItem from meeting information
        """
        topic = meeting_info.get('topic', '')
        time_str = meeting_info.get('time', '')
        location = meeting_info.get('location', '')
        organizer = meeting_info.get('organizer', '')
        participants = meeting_info.get('participants', '')
        week_info = meeting_info.get('week', '')

        if not topic:
            return

        # Build title
        title = topic
        if time_str and time_str not in topic:
            title = f"[{time_str}] {topic}"

        # Build content
        content_parts = []

        if week_info:
            content_parts.append(f"周次: {week_info}")
        if time_str:
            content_parts.append(f"时间: {time_str}")
        if location:
            content_parts.append(f"地点: {location}")
        if organizer:
            content_parts.append(f"主办单位: {organizer}")
        if participants:
            content_parts.append(f"参加人员: {participants}")

        content_parts.append(f"\n会议内容: {topic}")

        content = '\n'.join(content_parts)

        # Parse date from time string
        published_at = self.parse_meeting_date(time_str)

        # Generate summary
        summary = content[:200] + '...' if len(content) > 200 else content

        # Generate content hash
        content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

        yield NewsItem(
            title=self.clean_html(title),
            content=content,
            summary=summary,
            source_url=response.url,
            source_name='武汉理工大学周会安排',
            published_at=published_at,
            author=None,
            publisher=organizer.strip() if organizer else None,
            images=[],
            attachments=[],
            category='会议安排',
            department=organizer.strip() if organizer else None,
            tags=['会议', '周会', '日程'],
            content_hash=content_hash,
        )
        self.logger.info(f'Created meeting item: {title[:50]}...')

    def clean_html(self, text):
        """
        Clean HTML tags and extra whitespace
        """
        if not text:
            return text

        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def parse_meeting_date(self, time_str):
        """
        Parse meeting date from time string
        """
        if not time_str:
            return None

        try:
            # Try various patterns
            # Pattern: "12月22日" or "2024年12月22日"
            match = re.search(r'(\d{4})?年?(\d{1,2})月(\d{1,2})日', time_str)
            if match:
                year = int(match.group(1)) if match.group(1) else datetime.now().year
                month = int(match.group(2))
                day = int(match.group(3))
                return datetime(year, month, day).isoformat()

            # Pattern: "2024-12-22"
            match = re.search(r'(\d{4})-(\d{2})-(\d{2})', time_str)
            if match:
                return datetime.strptime(match.group(0), '%Y-%m-%d').isoformat()

        except Exception as e:
            self.logger.warning(f'Failed to parse meeting date: {time_str}, error: {e}')

        return None
