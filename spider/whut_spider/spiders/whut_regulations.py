import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape


class WhutRegulationsSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology Regulations Database (https://zd.whut.edu.cn)

    Categories:
    - 党委制度 (dwzd) - Party Committee Regulations
    - 行政制度 (xzzd) - Administrative Regulations
    - 纪委制度 (jwzd) - Discipline Inspection Regulations
    - 二级单位制度 (deptism) - Secondary Unit Regulations
    - 制度解读 (interpretation) - Policy Interpretation
    """
    name = 'whut_regulations'
    allowed_domains = ['zd.whut.edu.cn']

    # Category mappings
    CATEGORIES = {
        'dwzd': '党委制度',
        'xzzd': '行政制度',
        'jwzd': '纪委制度',
        'deptism': '二级单位制度',
        'interpretation': '制度解读',
    }

    start_urls = [
        'https://zd.whut.edu.cn/',
    ]

    # Track visited URLs
    visited_urls = set()

    # Maximum pages per category
    max_pages_per_category = 3

    def parse(self, response):
        """
        Parse homepage and follow category links
        """
        self.logger.info(f'Parsing regulations homepage: {response.url}')

        # Follow each category
        for cat_code, cat_name in self.CATEGORIES.items():
            cat_url = f'https://zd.whut.edu.cn/{cat_code}/'
            if cat_url not in self.visited_urls:
                self.visited_urls.add(cat_url)
                yield scrapy.Request(
                    cat_url,
                    callback=self.parse_category_page,
                    meta={'category': cat_name, 'cat_code': cat_code, 'page': 0}
                )

    def parse_category_page(self, response):
        """
        Parse regulation category listing page
        """
        category = response.meta.get('category', '行政制度')
        cat_code = response.meta.get('cat_code')
        current_page = response.meta.get('page', 0)

        self.logger.info(f'Parsing category "{category}" page {current_page}: {response.url}')

        # Extract regulation items
        # Try table-based layout first (common for regulations)
        rows = response.css('table tr, ul.list li, div.list li')

        item_count = 0
        for row in rows:
            # Skip header rows
            if row.css('th'):
                continue

            link = row.css('a::attr(href)').get()
            if not link:
                continue

            # Skip non-article links
            if link.startswith('javascript') or link == '#':
                continue
            if not link.endswith('.shtml') and not link.endswith('.htm'):
                continue

            title = row.css('a::attr(title)').get()
            if not title:
                title = row.css('a::text').get()

            # Extract date (usually in last column or span)
            date_str = row.css('td:last-child::text, span.date::text').get()
            if not date_str:
                row_text = row.get()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', row_text)
                if date_match:
                    date_str = date_match.group(1)

            if link and title:
                full_url = response.urljoin(link)
                if full_url not in self.visited_urls:
                    self.visited_urls.add(full_url)
                    item_count += 1
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_regulation,
                        meta={
                            'title': title.strip() if title else None,
                            'date_str': date_str.strip() if date_str else None,
                            'category': category
                        }
                    )

        self.logger.info(f'Found {item_count} regulations on {category} page {current_page}')

        # Handle pagination
        if current_page < self.max_pages_per_category:
            next_page_url = self.get_next_page_url(response, cat_code, current_page)
            if next_page_url and next_page_url not in self.visited_urls:
                self.visited_urls.add(next_page_url)
                yield scrapy.Request(
                    next_page_url,
                    callback=self.parse_category_page,
                    meta={
                        'category': category,
                        'cat_code': cat_code,
                        'page': current_page + 1
                    }
                )

    def get_next_page_url(self, response, cat_code, current_page):
        """
        Construct next page URL
        """
        # Look for createPageHTML pattern
        page_match = re.search(r'createPageHTML\((\d+),\s*(\d+)', response.text)
        if page_match:
            total_pages = int(page_match.group(1))
            current_idx = int(page_match.group(2))
            if current_idx + 1 < total_pages:
                next_idx = current_idx + 1
                if next_idx == 0:
                    return f'https://zd.whut.edu.cn/{cat_code}/index.shtml'
                return f'https://zd.whut.edu.cn/{cat_code}/index_{next_idx}.shtml'

        # Try explicit next link
        next_link = response.css('a.next::attr(href), a:contains("下一页")::attr(href)').get()
        if next_link:
            return response.urljoin(next_link)

        return None

    def parse_regulation(self, response):
        """
        Parse individual regulation/policy document page
        Note: Many regulations are PDFs displayed via PDF.js, not HTML content
        """
        title = response.meta.get('title')
        date_str = response.meta.get('date_str')
        category = response.meta.get('category', '行政制度')

        # Get title from page if not provided
        if not title:
            title = response.css('h1::text, div.title::text, div.article-title::text').get()
            if title:
                title = title.strip()

        # Extract document number if present
        doc_number = None
        doc_match = re.search(r'([（(]\s*[\u4e00-\u9fa5]+\s*[〔\[]\s*\d{4}\s*[〕\]]\s*\d+\s*号\s*[）)])', title or '')
        if doc_match:
            doc_number = doc_match.group(1)

        # Extract content
        content_parts = []

        content_selectors = [
            'div.v_news_content',
            'div.article-content',
            'div.content',
            'div.TRS_Editor',
            'div.wp_articlecontent',
            'article',
        ]

        for selector in content_selectors:
            paragraphs = response.css(f'{selector} p')
            if paragraphs:
                for p in paragraphs:
                    p_text = ' '.join(p.css('*::text, ::text').getall())
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if p_text and len(p_text) > 5:
                        content_parts.append(p_text)
                if content_parts:
                    break

        # Fallback: get all text from content div
        if not content_parts:
            for selector in content_selectors:
                content_div = response.css(f'{selector}').get()
                if content_div:
                    text = re.sub(r'<[^>]+>', ' ', content_div)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 50:
                        content_parts = [text]
                        break

        content = '\n\n'.join(content_parts) if content_parts else ''
        content = self.clean_html(content)

        # Extract date from page
        if not date_str:
            date_str = response.css('span.date::text, div.info span::text').get()
            if not date_str:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', response.text)
                if date_match:
                    date_str = date_match.group(1)

        published_at = self.parse_date(date_str) if date_str else None

        # Extract issuing department
        publisher = None
        issuer_match = re.search(r'(发布单位|发文单位|制定部门)[：:]\s*([^\s\u3000<|]+)', response.text)
        if issuer_match:
            publisher = issuer_match.group(2)

        # Extract attachments (regulations often have PDF/DOC attachments)
        attachments = []
        attachment_links = response.css(
            'a[href$=".pdf"], a[href$=".doc"], a[href$=".docx"], '
            'a[href$=".xls"], a[href$=".xlsx"], div.attachment a, '
            'div.article-enclosure a'
        )
        for link in attachment_links[:10]:
            href = link.css('::attr(href)').get()
            name = link.css('::text').get()
            if href:
                attachments.append({
                    'name': name.strip() if name else href.split('/')[-1],
                    'url': response.urljoin(href)
                })

        # Also check for PDF in JavaScript (PDF.js rendering)
        pdf_match = re.search(r'showPdf\(["\']([^"\']+\.pdf)["\']', response.text)
        if pdf_match:
            pdf_url = response.urljoin(pdf_match.group(1))
            if not any(a['url'] == pdf_url for a in attachments):
                attachments.append({
                    'name': title + '.pdf' if title else 'document.pdf',
                    'url': pdf_url
                })

        # If no HTML content but we have attachments, create placeholder content
        if (not content or len(content) < 20) and attachments:
            content = f"[PDF文档] 本规章制度为PDF格式文件，请下载附件查看完整内容。"
            if title:
                content = f"[PDF文档] {title}\n\n本规章制度为PDF格式文件，请下载附件查看完整内容。"

        # Skip if still no content and no attachments
        if (not content or len(content) < 20) and not attachments:
            self.logger.warning(f'No content or attachments found for regulation: {response.url}')
            return

        # Generate summary
        summary = content[:200] + '...' if len(content) > 200 else content
        summary = self.clean_html(summary)

        # Generate content hash
        content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

        # Add document number to title if found
        if doc_number and doc_number not in (title or ''):
            title = f"{title} {doc_number}"

        if title and content:
            yield NewsItem(
                title=self.clean_html(title),
                content=content,
                summary=summary,
                source_url=response.url,
                source_name='武汉理工大学规章制度库',
                published_at=published_at,
                author=None,
                publisher=publisher.strip() if publisher else None,
                images=[],
                attachments=attachments,
                category=category,
                department=None,
                tags=['制度', '规章'],
                content_hash=content_hash,
            )
            self.logger.info(f'Successfully scraped regulation: {title[:50]}...')

    def clean_html(self, text):
        """
        Clean HTML tags and extra whitespace
        """
        if not text:
            return text

        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s*class\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', '', text)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def parse_date(self, date_str):
        """
        Parse date string to ISO format
        """
        if not date_str:
            return None

        try:
            date_str = date_str.strip()

            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y-%m-%d').isoformat()

            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).isoformat()

            if re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y/%m/%d').isoformat()

        except Exception as e:
            self.logger.warning(f'Failed to parse date: {date_str}, error: {e}')

        return None
