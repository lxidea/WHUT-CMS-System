import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape


class WhutNewsPortalSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology Official News Portal (https://news.whut.edu.cn)

    Categories:
    - 综合新闻 (zhxw) - General News
    - 理工资讯 (lgzx) - Institute Updates
    - 学术动态 (xsdt) - Academic Updates
    - 文化影像 (whyx) - Culture & Media
    - 校园生活 (xysh) - Campus Life
    - 媒体理工 (mtlg) - Media Coverage
    - 校园人物 (xyrw) - Campus People
    - 通知公告 (tzgg) - Announcements
    - 视频新闻 (spxw) - Video News
    """
    name = 'whut_news_portal'
    allowed_domains = ['news.whut.edu.cn']

    # Category mappings
    CATEGORIES = {
        'zhxw': '综合新闻',
        'lgzx': '理工资讯',
        'xsdt': '学术动态',
        'whyx': '文化影像',
        'xysh': '校园生活',
        'mtlg': '媒体理工',
        'xyrw': '校园人物',
        'tzgg': '通知公告',
        'spxw': '视频新闻',
    }

    start_urls = [
        'https://news.whut.edu.cn/',
    ]

    # Track visited URLs to avoid duplicates
    visited_urls = set()

    # Maximum pages to crawl per category
    max_pages_per_category = 5

    def parse(self, response):
        """
        Parse homepage and follow category links
        """
        self.logger.info(f'Parsing homepage: {response.url}')

        # Parse featured news on homepage
        yield from self.parse_homepage_news(response)

        # Follow each category page
        for cat_code, cat_name in self.CATEGORIES.items():
            cat_url = f'https://news.whut.edu.cn/{cat_code}/'
            if cat_url not in self.visited_urls:
                self.visited_urls.add(cat_url)
                yield scrapy.Request(
                    cat_url,
                    callback=self.parse_category_page,
                    meta={'category': cat_name, 'cat_code': cat_code, 'page': 1}
                )

    def parse_homepage_news(self, response):
        """
        Extract featured news from homepage
        """
        # Featured articles in various sections
        # Try multiple selectors for different homepage layouts

        # Main featured area
        featured_links = response.css('div.bd ul li a::attr(href)').getall()
        featured_titles = response.css('div.bd ul li a::text, div.bd ul li h3::text').getall()

        for i, link in enumerate(featured_links[:20]):  # Limit to first 20 featured
            if link and not link.startswith('javascript'):
                full_url = response.urljoin(link)
                if full_url not in self.visited_urls:
                    self.visited_urls.add(full_url)
                    title = featured_titles[i].strip() if i < len(featured_titles) else None
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_article,
                        meta={
                            'title': title,
                            'category': self.extract_category_from_url(full_url)
                        }
                    )

    def parse_category_page(self, response):
        """
        Parse category listing page
        """
        category = response.meta.get('category', '综合新闻')
        cat_code = response.meta.get('cat_code')
        current_page = response.meta.get('page', 1)

        self.logger.info(f'Parsing category "{category}" page {current_page}: {response.url}')

        # Extract news items from list
        # Common patterns: ul li with links, table rows, div lists
        news_items = response.css('ul.news_list li, div.news_list li, ul li')

        if not news_items:
            # Try table-based layout
            news_items = response.css('table tr')

        item_count = 0
        for item in news_items:
            link = item.css('a::attr(href)').get()
            if not link:
                continue

            # Skip navigation and non-article links
            if link.startswith('javascript') or link.startswith('#') or link == '#':
                continue
            if 'javascript:' in link.lower():
                continue
            if not re.search(r't\d+_\d+\.shtml', link) and not link.endswith('.shtml'):
                continue

            title = item.css('a::attr(title)').get()
            if not title:
                title = item.css('a::text').get()
            if not title:
                title = item.css('h3::text, h4::text').get()

            # Extract date if available
            date_str = item.css('span.date::text, td:last-child::text').get()
            if not date_str:
                # Try to find date pattern in text
                item_text = item.get()
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', item_text)
                if date_match:
                    date_str = date_match.group(1)

            if link and title:
                full_url = response.urljoin(link)
                if full_url not in self.visited_urls:
                    self.visited_urls.add(full_url)
                    item_count += 1
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_article,
                        meta={
                            'title': title.strip() if title else None,
                            'date_str': date_str.strip() if date_str else None,
                            'category': category
                        }
                    )

        self.logger.info(f'Found {item_count} articles on {category} page {current_page}')

        # Follow pagination if within limits
        if current_page < self.max_pages_per_category:
            # Try to find next page link
            next_page = self.get_next_page_url(response, cat_code, current_page)
            if next_page and next_page not in self.visited_urls:
                self.visited_urls.add(next_page)
                yield scrapy.Request(
                    next_page,
                    callback=self.parse_category_page,
                    meta={
                        'category': category,
                        'cat_code': cat_code,
                        'page': current_page + 1
                    }
                )

    def get_next_page_url(self, response, cat_code, current_page):
        """
        Construct next page URL based on common pagination patterns
        """
        if not cat_code:
            return None

        # Pattern 1: index_N.shtml where N decrements
        # Try to find pagination info in page
        page_match = re.search(r'createPageHTML\((\d+),\s*(\d+)', response.text)
        if page_match:
            total_pages = int(page_match.group(1))
            current_idx = int(page_match.group(2))
            if current_idx + 1 < total_pages:
                next_idx = current_idx + 1
                return f'https://news.whut.edu.cn/{cat_code}/index_{next_idx}.shtml'
            # No more pages
            return None

        # Pattern 2: Look for explicit next page link
        next_link = response.css('a.next::attr(href), a:contains("下一页")::attr(href)').get()
        if next_link and not next_link.startswith('javascript') and next_link != '#':
            return response.urljoin(next_link)

        # Don't guess - only return None if we don't have clear pagination info
        return None

    def parse_article(self, response):
        """
        Parse individual article page
        """
        title = response.meta.get('title')
        date_str = response.meta.get('date_str')
        category = response.meta.get('category', '综合新闻')

        # Try to get title from page if not provided or too short (truncated)
        if not title or len(title.strip()) < 5:
            # Try CSS selectors first
            title = response.css('h1::text, div.title::text, div.article-title::text').get()
            if title:
                title = title.strip()

            # Fall back to page <title> tag
            if not title or len(title) < 5:
                page_title = response.css('title::text').get()
                if page_title:
                    # Remove common suffixes like "-武汉理工大学新闻经纬"
                    page_title = re.sub(r'-[^-]+$', '', page_title).strip()
                    if len(page_title) >= 5:
                        title = page_title

        # Extract content
        content_parts = []

        # Common content selectors for news.whut.edu.cn
        content_selectors = [
            'div.v_news_content',
            'div.article-content',
            'div.content',
            'div.TRS_Editor',
            'div.news_content',
            'article',
        ]

        for selector in content_selectors:
            paragraphs = response.css(f'{selector} p')
            if paragraphs:
                for p in paragraphs:
                    p_text = ' '.join(p.css('*::text, ::text').getall())
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if p_text and len(p_text) > 10:  # Skip very short fragments
                        content_parts.append(p_text)
                if content_parts:
                    break

        # If no paragraphs, try getting all text from content div
        if not content_parts:
            for selector in content_selectors:
                content_div = response.css(f'{selector}').get()
                if content_div:
                    # Extract text, removing tags
                    text = re.sub(r'<[^>]+>', ' ', content_div)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 50:
                        content_parts = [text]
                        break

        content = '\n\n'.join(content_parts) if content_parts else ''
        content = self.clean_html(content)

        # Skip if no meaningful content
        if not content or len(content) < 20:
            self.logger.warning(f'No content found for: {response.url}')
            return

        # Extract date from page if not provided
        if not date_str:
            date_str = response.css('span.date::text, div.info span::text').get()
            if not date_str:
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', response.text)
                if date_match:
                    date_str = date_match.group(1)

        published_at = self.parse_date(date_str) if date_str else None

        # Extract author
        author = None
        author_match = re.search(r'(作者|记者|撰稿|编辑)[：:]\s*([^\s\u3000<]+)', response.text)
        if author_match:
            author = author_match.group(2)

        # Extract source/publisher
        publisher = None
        source_match = re.search(r'(来源|供稿|发布)[：:]\s*([^\s\u3000<|]+)', response.text)
        if source_match:
            publisher = source_match.group(2)

        # Extract images
        images = response.css(
            'div.v_news_content img::attr(src), '
            'div.article-content img::attr(src), '
            'div.content img::attr(src)'
        ).getall()
        images = [response.urljoin(img) for img in images if img and not img.endswith('.gif')]

        # Generate summary
        summary = content[:200] + '...' if len(content) > 200 else content
        summary = self.clean_html(summary)

        # Generate content hash
        content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

        if title and content:
            yield NewsItem(
                title=self.clean_html(title),
                content=content,
                summary=summary,
                source_url=response.url,
                source_name='武汉理工大学新闻网',
                published_at=published_at,
                author=author.strip() if author else None,
                publisher=publisher.strip() if publisher else None,
                images=images[:5],  # Limit images
                attachments=[],
                category=category,
                department=None,
                tags=[],
                content_hash=content_hash,
            )
            self.logger.info(f'Successfully scraped: {title[:50]}...')

    def extract_category_from_url(self, url):
        """
        Extract category name from URL path
        """
        for code, name in self.CATEGORIES.items():
            if f'/{code}/' in url:
                return name
        return '综合新闻'

    def clean_html(self, text):
        """
        Clean HTML tags and extra whitespace from text
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
        Parse various date formats
        """
        if not date_str:
            return None

        try:
            date_str = date_str.strip()

            # Format: "2025-12-22"
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y-%m-%d').isoformat()

            # Format: "2025年12月22日"
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).isoformat()

            # Format: "2025/12/22"
            if re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y/%m/%d').isoformat()

        except Exception as e:
            self.logger.warning(f'Failed to parse date: {date_str}, error: {e}')

        return None
