import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape


class WhutYouthSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology Youth League Website
    (http://youth.whut.edu.cn/)

    Youth League websites typically have sections like:
    - 首页 - Homepage
    - 青年学习 - Youth Study
    - 通知公告 - Announcements
    - 团学动态 - League Dynamics
    - 基层风采 - Grassroots Highlights
    - 志愿服务 - Volunteer Service
    - 社会实践 - Social Practice
    - 创新创业 - Innovation & Entrepreneurship
    - 文化艺术 - Culture & Arts
    - 规章制度 - Regulations

    Note: This spider may require internal network access.
    """
    name = 'whut_youth'
    allowed_domains = ['youth.whut.edu.cn']

    # Common Youth League website category patterns
    CATEGORIES = {
        'tzgg': '通知公告',
        'txdt': '团学动态',
        'qnxx': '青年学习',
        'jcfc': '基层风采',
        'zyfw': '志愿服务',
        'shsj': '社会实践',
        'cxcy': '创新创业',
        'whys': '文化艺术',
        'gzzd': '规章制度',
        'xydt': '学院动态',
        'xwdt': '新闻动态',
    }

    start_urls = [
        'http://youth.whut.edu.cn/',
    ]

    # Track visited URLs
    visited_urls = set()

    # Maximum pages per category
    max_pages_per_category = 5

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    }

    def parse(self, response):
        """
        Parse homepage and discover category pages
        """
        self.logger.info(f'Parsing Youth League homepage: {response.url}')

        # Extract news from homepage
        yield from self.parse_homepage_news(response)

        # Discover category pages from navigation
        nav_links = response.css('nav a::attr(href), div.nav a::attr(href), ul.menu a::attr(href)').getall()

        for link in nav_links:
            if not link or link.startswith('javascript') or link == '#':
                continue

            full_url = response.urljoin(link)
            if full_url not in self.visited_urls:
                # Check if this looks like a category page
                for cat_code in self.CATEGORIES.keys():
                    if cat_code in link.lower() or f'/{cat_code}/' in link:
                        self.visited_urls.add(full_url)
                        yield scrapy.Request(
                            full_url,
                            callback=self.parse_category_page,
                            meta={
                                'category': self.CATEGORIES.get(cat_code, '团学动态'),
                                'cat_code': cat_code,
                                'page': 0
                            }
                        )
                        break

        # Also try common category URL patterns
        for cat_code, cat_name in self.CATEGORIES.items():
            for pattern in [f'/{cat_code}/', f'/{cat_code}/index.shtml', f'/{cat_code}.htm']:
                cat_url = f'http://youth.whut.edu.cn{pattern}'
                if cat_url not in self.visited_urls:
                    self.visited_urls.add(cat_url)
                    yield scrapy.Request(
                        cat_url,
                        callback=self.parse_category_page,
                        meta={
                            'category': cat_name,
                            'cat_code': cat_code,
                            'page': 0
                        },
                        dont_filter=True,
                        errback=self.handle_error
                    )

    def handle_error(self, failure):
        """
        Handle request errors silently (category may not exist)
        """
        self.logger.debug(f'Failed to fetch: {failure.request.url}')

    def parse_homepage_news(self, response):
        """
        Extract news items from homepage
        """
        # Try various common selectors
        news_sections = response.css(
            'div.news-list, '
            'div.article-list, '
            'ul.news-list, '
            'div.list_box, '
            'div.bd ul'
        )

        for section in news_sections:
            items = section.css('li, div.item')
            for item in items:
                link = item.css('a::attr(href)').get()
                if not link or link.startswith('javascript'):
                    continue

                title = item.css('a::attr(title)').get()
                if not title:
                    title = item.css('a::text').get()
                if not title:
                    continue

                title = title.strip()
                if len(title) < 5:
                    continue

                date_str = item.css('span.date::text, span::text').get()

                full_url = response.urljoin(link)
                if full_url not in self.visited_urls:
                    self.visited_urls.add(full_url)
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_article,
                        meta={
                            'title': title,
                            'date_str': date_str,
                            'category': '团学动态'
                        }
                    )

    def parse_category_page(self, response):
        """
        Parse category listing page
        """
        category = response.meta.get('category', '团学动态')
        cat_code = response.meta.get('cat_code')
        current_page = response.meta.get('page', 0)

        self.logger.info(f'Parsing Youth category "{category}" page {current_page}: {response.url}')

        # Extract news items
        item_count = 0

        # Try multiple selectors
        items = response.css(
            'ul.news_list li, '
            'ul.normal_list li, '
            'div.list li, '
            'table tr, '
            'ul li'
        )

        for item in items:
            # Skip header rows
            if item.css('th'):
                continue

            link = item.css('a::attr(href)').get()
            if not link:
                continue

            if link.startswith('javascript') or link == '#':
                continue

            # Filter to article-like links
            if not (link.endswith('.shtml') or link.endswith('.htm') or link.endswith('.html') or '/t' in link):
                continue

            title = item.css('a::attr(title)').get()
            if not title:
                title = item.css('a::text').get()

            if not title or len(title.strip()) < 5:
                continue

            title = title.strip()

            # Extract date
            date_str = item.css('span.date::text, td:last-child::text, span::text').get()
            if not date_str:
                item_html = item.get()
                date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', item_html)
                if date_match:
                    date_str = date_match.group(1)

            full_url = response.urljoin(link)
            if full_url not in self.visited_urls:
                self.visited_urls.add(full_url)
                item_count += 1
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title,
                        'date_str': date_str,
                        'category': category
                    }
                )

        self.logger.info(f'Found {item_count} articles on {category} page {current_page}')

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
                    return f'http://youth.whut.edu.cn/{cat_code}/index.shtml'
                return f'http://youth.whut.edu.cn/{cat_code}/index_{next_idx}.shtml'

        # Try explicit next link
        next_link = response.css('a.next::attr(href), a:contains("下一页")::attr(href)').get()
        if next_link:
            return response.urljoin(next_link)

        return None

    def parse_article(self, response):
        """
        Parse individual article page
        """
        title = response.meta.get('title')
        date_str = response.meta.get('date_str')
        category = response.meta.get('category', '团学动态')

        # Get title from page if not provided
        if not title:
            title = response.css(
                'h1::text, '
                'div.title::text, '
                'div.article-title::text, '
                '.detail-title::text'
            ).get()
            if title:
                title = title.strip()

        # Extract content
        content_parts = []
        content_selectors = [
            'div.v_news_content',
            'div.article-content',
            'div.content',
            'div.TRS_Editor',
            'div.wp_articlecontent',
            'div#content',
            'article',
        ]

        for selector in content_selectors:
            paragraphs = response.css(f'{selector} p')
            if paragraphs:
                for p in paragraphs:
                    p_text = ' '.join(p.css('*::text, ::text').getall())
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if p_text and len(p_text) > 10:
                        content_parts.append(p_text)
                if content_parts:
                    break

        # Fallback
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

        # Skip if no content
        if not content or len(content) < 20:
            self.logger.warning(f'No content found: {response.url}')
            return

        # Extract date from page if not provided
        if not date_str:
            date_str = response.css('span.date::text, div.info span::text').get()
            if not date_str:
                date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', response.text)
                if date_match:
                    date_str = date_match.group(1)

        published_at = self.parse_date(date_str) if date_str else None

        # Extract author
        author = None
        author_match = re.search(r'(作者|撰稿|编辑|供稿)[：:]\s*([^\s\u3000<]+)', response.text)
        if author_match:
            author = author_match.group(2)

        # Extract publisher
        publisher = None
        source_match = re.search(r'(来源|发布)[：:]\s*([^\s\u3000<|]+)', response.text)
        if source_match:
            publisher = source_match.group(2)

        # Extract images
        images = response.css(
            'div.article-content img::attr(src), '
            'div.content img::attr(src), '
            'div.TRS_Editor img::attr(src)'
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
                source_name='武汉理工大学共青团',
                published_at=published_at,
                author=author.strip() if author else None,
                publisher=publisher.strip() if publisher else None,
                images=images[:5],
                attachments=[],
                category=category,
                department=None,
                tags=['共青团', '青年'],
                content_hash=content_hash,
            )
            self.logger.info(f'Successfully scraped: {title[:50]}...')

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
