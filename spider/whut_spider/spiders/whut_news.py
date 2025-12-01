import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape

class WhutNewsSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology news website (http://i.whut.edu.cn)

    Phase 5: Comprehensive crawling - extracts news from all categories, departments, and colleges
    """
    name = 'whut_news'
    allowed_domains = ['i.whut.edu.cn', 'whut.edu.cn', 'news.whut.edu.cn']

    start_urls = [
        'http://i.whut.edu.cn',                  # Homepage
        'http://i.whut.edu.cn/xxtg/',           # School Notices (133 pages)
        'http://i.whut.edu.cn/bmxw/',           # Department Highlights
        'http://i.whut.edu.cn/xytg/',           # College Notices
        'http://i.whut.edu.cn/xyxw/',           # College News
    ]

    # Track visited URLs to avoid duplicates
    visited_urls = set()

    def parse(self, response):
        """
        Route to appropriate parser based on URL
        """
        self.logger.info(f'Parsing URL: {response.url}')

        # Homepage - parse news sections
        if response.url == 'http://i.whut.edu.cn' or response.url == 'http://i.whut.edu.cn/':
            yield from self.parse_homepage(response)
        # Category pages with sidebar navigation
        elif any(cat in response.url for cat in ['/xxtg/', '/bmxw/', '/xytg/', '/xyxw/']):
            yield from self.parse_category(response)
        else:
            self.logger.warning(f'No parser for URL: {response.url}')

    def parse_homepage(self, response):
        """
        Parse homepage and extract news from all list_box sections
        """
        self.logger.info(f'Parsing homepage: {response.url}')

        # Find all news list boxes on homepage
        news_sections = response.css('div.list_box1, div.list_box1.f10')
        self.logger.info(f'Found {len(news_sections)} news sections')

        for section in news_sections:
            # Get section title/category
            category = section.css('div.tit_box2 h2::text').get()
            if category:
                category = category.strip()
            else:
                category = '综合新闻'

            # Get all news items in this section
            news_items = section.css('ul li')
            self.logger.info(f'Section "{category}": found {len(news_items)} items')

            for item in news_items:
                link = item.css('a::attr(href)').get()
                title = item.css('a::attr(title)').get()
                if not title:
                    title = item.css('a::text').get()
                date_str = item.css('span::text').get()

                if link and title:
                    full_url = response.urljoin(link)
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_article,
                        meta={
                            'title': title.strip(),
                            'date_str': date_str.strip() if date_str else None,
                            'category': category
                        }
                    )

    def parse_article(self, response):
        """
        Parse individual news article page
        """
        # Get metadata passed from parse()
        title = response.meta.get('title')
        date_str = response.meta.get('date_str')
        category = response.meta.get('category', '综合新闻')
        department = response.meta.get('department')

        # Try to extract department from title if not already set
        if not department:
            department = self.extract_department_from_title(title)

        # Extract content from article body
        # Try multiple common selectors
        content_parts = []

        # Method 1: Common content div patterns
        # Extract paragraph elements, then get all text from each paragraph
        content_div_selectors = [
            'div.TRS_Editor',         # TRS CMS (WHUT uses this)
            'div.article-content',
            'div.content',
            'div.article-body',
            'div.article',
            'div.wp_articlecontent',  # Common in Chinese CMS
            'div#vsb_content',        # VSB system
            'div.text',
            'article',
        ]

        content_parts = []
        for div_selector in content_div_selectors:
            # Get all paragraph elements
            paragraphs = response.css(f'{div_selector} p')
            if paragraphs:
                # For each paragraph, extract all text (including nested tags)
                for p in paragraphs:
                    # Get all text nodes within this paragraph
                    p_text = ' '.join(p.css('*::text, ::text').getall())
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if p_text:
                        content_parts.append(p_text)
                if content_parts:
                    break

        # Join paragraphs with double newline
        content = '\n\n'.join(content_parts) if content_parts else ''

        # If still no content, try XPath to get all text from likely content area
        if not content:
            # Try to get all text from main content divs
            content_xpath = response.xpath(
                '//div[contains(@class, "content")]//text() | '
                '//div[contains(@class, "article")]//text() | '
                '//div[@id="vsb_content"]//text() | '
                '//div[@class="TRS_Editor"]//text()'
            ).getall()
            if content_xpath:
                content = ' '.join([t.strip() for t in content_xpath if t.strip()])
                content = re.sub(r'\s+', ' ', content).strip()

        # Clean HTML tags and CSS class names from content
        content = self.clean_html(content)

        # If STILL no content, create placeholder from title for image-only posts
        if not content and title:
            # Extract image alt texts as fallback content
            img_alts = response.css('div.TRS_Editor img::attr(alt)').getall()
            if img_alts:
                img_text = '; '.join([alt.strip() for alt in img_alts if alt.strip()])
                content = f"[图片公告] {img_text}" if img_text else f"[图片公告] {title}"
            else:
                # For pure image announcements, use title as content
                content = f"[图片公告] 详见附图"

        # Parse date
        published_at = self.parse_date(date_str) if date_str else None

        # Extract author if present
        author = response.css('span.author::text, div.author::text').get()
        if not author:
            # Try to find author in common patterns
            author_match = re.search(r'(作者|撰稿|编辑)[：:]\s*([^\s\u3000]+)', response.text)
            if author_match:
                author = author_match.group(2)

        # Extract publisher (publishing unit/department)
        publisher = None

        # Method 1: Look for common publisher labels
        publisher_match = re.search(r'(来源|发布单位|供稿|单位|发布部门|发布者)[：:]\s*([^\s\u3000\|]+)', response.text)
        if publisher_match:
            publisher = publisher_match.group(2).strip()

        # Method 2: If not found, try CSS selectors
        if not publisher:
            publisher = response.css('span.source::text, div.source::text, span.publisher::text').get()

        # Method 3: Try to extract from metadata section
        if not publisher:
            # Look for publisher in page metadata
            meta_section = response.css('div.xl-tie p, div.article-meta').getall()
            for meta_html in meta_section:
                pub_match = re.search(r'(来源|发布单位|供稿)[：:]([^<\s]+)', meta_html)
                if pub_match:
                    publisher = pub_match.group(2).strip()
                    break

        # Extract images
        images = response.css(
            'div.article-content img::attr(src), '
            'div.content img::attr(src), '
            'div.wp_articlecontent img::attr(src), '
            'div#vsb_content img::attr(src), '
            'article img::attr(src)'
        ).getall()
        images = [response.urljoin(img) for img in images if img and not img.endswith('.gif')]

        # Clean title
        title = self.clean_html(title) if title else title

        # Generate summary from first 200 chars of content
        summary = None
        if content:
            summary = content[:200] + '...' if len(content) > 200 else content
            summary = self.clean_html(summary)

        # Extract attachments if any
        attachments = []
        attachment_links = response.css(
            'div.attachments a, '
            'div.attachment a, '
            'a[href$=".pdf"], '
            'a[href$=".doc"], '
            'a[href$=".docx"], '
            'a[href$=".xls"], '
            'a[href$=".xlsx"]'
        )
        for link in attachment_links[:10]:  # Limit to 10 attachments
            href = link.css('::attr(href)').get()
            name = link.css('::text').get()
            if href:
                attachments.append({
                    'name': name.strip() if name else href.split('/')[-1],
                    'url': response.urljoin(href)
                })

        # Generate content hash for deduplication
        content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

        # Only yield if we have minimum required data
        if title and content:
            yield NewsItem(
                title=title,
                content=content,
                summary=summary,
                source_url=response.url,
                source_name='武汉理工大学',
                published_at=published_at,
                author=author.strip() if author else None,
                publisher=publisher.strip() if publisher else None,  # Include publisher field
                images=images,
                attachments=attachments,
                category=category,
                department=department,  # Include department field
                tags=[],
                content_hash=content_hash,
            )
            self.logger.info(f'Successfully scraped: {title[:50]}...')
        else:
            self.logger.warning(f'Incomplete data for URL: {response.url} (title: {bool(title)}, content: {bool(content)})')

    def clean_html(self, text):
        """
        Clean HTML tags, CSS class names, and extra whitespace from text
        """
        if not text:
            return text

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove CSS class attributes like class="TRS_Editor"
        text = re.sub(r'\s*class\s*=\s*["\'][^"\']*["\']', '', text)
        text = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', '', text)

        # Remove common CMS markers and class names
        text = re.sub(r'\.TRS_Editor\b', '', text)
        text = re.sub(r'\bTRS_Editor\b', '', text)
        text = re.sub(r'\.(wp_articlecontent|vsb_content|article-content)\b', '', text)

        # Remove JavaScript and CSS remnants
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML entities
        text = unescape(text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def parse_category(self, response):
        """
        Parse category page with sidebar navigation and article list
        """
        self.logger.info(f'Parsing category page: {response.url}')

        # Extract department/college links from sidebar
        dept_links = response.css('div.text_list_menu2 ul li a::attr(href)').getall()
        self.logger.info(f'Found {len(dept_links)} department/college links in sidebar')

        # Follow each department/college link
        for dept_url in dept_links:
            full_dept_url = response.urljoin(dept_url)
            if full_dept_url not in self.visited_urls:
                self.visited_urls.add(full_dept_url)
                yield scrapy.Request(
                    full_dept_url,
                    callback=self.parse_department,
                    meta={'category': self.extract_category(response.url)}
                )

        # Parse current page articles
        yield from self.parse_news_list(response)

        # Follow pagination
        yield from self.follow_pagination(response)

    def parse_department(self, response):
        """
        Parse individual department/college page
        """
        category = response.meta.get('category', '综合新闻')
        self.logger.info(f'Parsing department page: {response.url}')

        # Parse articles on this department page
        yield from self.parse_news_list(response)

        # Follow pagination
        yield from self.follow_pagination(response)

    def parse_news_list(self, response):
        """
        Extract news items from current page (works for both homepage and category pages)
        """
        # Try multiple selectors for different page layouts
        news_items = []

        # Homepage style (div.list_box1 ul li)
        homepage_items = response.css('div.list_box1 ul li, div.list_box1.f10 ul li')
        if homepage_items:
            news_items.extend(homepage_items)

        # Category page style (ul.normal_list2 li)
        category_items = response.css('ul.normal_list2 li')
        if category_items:
            news_items.extend(category_items)

        self.logger.info(f'Found {len(news_items)} news items on {response.url}')

        for item in news_items:
            # Extract link and title (try multiple selectors)
            link = item.css('a::attr(href)').get()
            if not link:
                link = item.css('span a:nth-child(2)::attr(href)').get()

            title = item.css('a::attr(title)').get()
            if not title:
                title = item.css('a::text').get()
            if not title:
                title = item.css('span a:nth-child(2)::attr(title)').get()

            # Extract date
            date_str = item.css('span::text').get()
            if not date_str:
                date_str = item.css('strong::text').get()

            # Extract category from response URL
            category = self.extract_category(response.url)

            # Extract department/college tag if present
            dept_tag = item.css('span i a::text').get()

            if link and title:
                full_url = response.urljoin(link)

                # Avoid duplicate requests
                if full_url in self.visited_urls:
                    continue
                self.visited_urls.add(full_url)

                yield scrapy.Request(
                    full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title.strip(),
                        'date_str': date_str.strip() if date_str else None,
                        'category': category,
                        'department': dept_tag.strip() if dept_tag else None
                    }
                )

    def follow_pagination(self, response):
        """
        Extract pagination info and follow next page
        """
        # Extract JavaScript pagination variables
        count_match = re.search(r'var countPage = (\d+);', response.text)
        current_match = re.search(r'var currentPage = (\d+);', response.text)

        if count_match and current_match:
            total_pages = int(count_match.group(1))
            current_page = int(current_match.group(1))

            self.logger.info(f'Pagination: page {current_page + 1}/{total_pages}')

            # Only follow a limited number of pages to avoid overload (e.g., first 10 pages)
            max_pages = 10
            if current_page < min(total_pages - 1, max_pages - 1):
                next_page_num = current_page + 1
                if next_page_num == 0:
                    next_url = response.urljoin('index.shtml')
                else:
                    next_url = response.urljoin(f'index_{next_page_num}.shtml')

                if next_url not in self.visited_urls:
                    self.visited_urls.add(next_url)
                    self.logger.info(f'Following pagination: {next_url}')
                    yield scrapy.Request(
                        next_url,
                        callback=self.parse_category if '/xxtg/' in response.url or '/bmxw/' in response.url or '/xytg/' in response.url or '/xyxw/' in response.url else self.parse_department,
                        meta=response.meta
                    )

    def extract_category(self, url):
        """
        Extract category name from URL
        """
        if '/xxtg/' in url:
            return '学校通知公告'
        elif '/bmxw/' in url:
            return '部门亮点资讯'
        elif '/xytg/' in url:
            return '学院通知公告'
        elif '/xyxw/' in url:
            return '学院新闻'
        elif 'news.whut.edu.cn' in url:
            return '综合新闻'
        else:
            return '综合新闻'

    def extract_department_from_title(self, title):
        """
        Extract department/college name from title with 【】 brackets
        """
        if not title:
            return None

        dept_match = re.search(r'【(.+?)】', title)
        if dept_match:
            return dept_match.group(1)

        return None

    def parse_date(self, date_str):
        """
        Parse various date formats found on WHUT website
        """
        if not date_str:
            return None

        try:
            # Clean the date string
            date_str = date_str.strip()

            # Format 1: "2025-11-28"
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y-%m-%d').isoformat()

            # Format 2: "2025年11月28日"
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).isoformat()

            # Format 3: "2025/11/28"
            if re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y/%m/%d').isoformat()

            # Format 4: "11-28" (assume current year - 2025)
            match = re.search(r'(\d{1,2})-(\d{1,2})', date_str)
            if match:
                month, day = match.groups()
                year = 2025  # Current year
                return datetime(year, int(month), int(day)).isoformat()

        except Exception as e:
            self.logger.warning(f'Failed to parse date: {date_str}, error: {e}')

        return None
