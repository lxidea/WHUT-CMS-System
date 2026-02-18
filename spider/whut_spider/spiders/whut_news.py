import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape

class WhutNewsSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology news website (http://i.whut.edu.cn)

    Rewritten for the redesigned site (~2025-12-22).
    """
    name = 'whut_news'
    allowed_domains = ['i.whut.edu.cn', 'whut.edu.cn', 'news.whut.edu.cn']

    start_urls = [
        'http://i.whut.edu.cn',                  # Homepage
        'http://i.whut.edu.cn/xxtg/',           # School Notices
        'http://i.whut.edu.cn/bmxw/',           # Department Highlights
        'http://i.whut.edu.cn/xytg/',           # College Notices
        'http://i.whut.edu.cn/lgjz/',           # Academic Lectures
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
        elif any(cat in response.url for cat in ['/xxtg/', '/bmxw/', '/xytg/', '/lgjz/']):
            yield from self.parse_category(response)
        else:
            self.logger.warning(f'No parser for URL: {response.url}')

    def parse_homepage(self, response):
        """
        Parse homepage and extract news from all sections on the redesigned site.
        Sections: headline carousel, image news carousel, tabbed news lists, notice lists.
        """
        self.logger.info(f'Parsing homepage: {response.url}')

        # --- a) Headline carousel ---
        headline_links = response.css('div.toutiao_box .swiper-slide .toutiao a')
        self.logger.info(f'Headline carousel: {len(headline_links)} items')
        for a in headline_links:
            link = a.css('::attr(href)').get()
            title = a.css('::text').get()
            if link and title:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title.strip(),
                        'date_str': None,
                        'category': '头条新闻',
                    }
                )

        # --- b) Image news carousel ---
        image_news = response.css('div.swiper_box .swiper-slide .news_box')
        self.logger.info(f'Image news carousel: {len(image_news)} items')
        for box in image_news:
            link = box.css('a.news_img_box::attr(href)').get()
            if not link:
                link = box.css('a::attr(href)').get()
            title = box.css('div.img_text2 a span.title::text').get()
            if not title:
                title = box.css('a::attr(title)').get()
            date_str = box.css('div.img_text2 a span.date::text').get()
            if link and title:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title.strip(),
                        'date_str': date_str.strip() if date_str else None,
                        'category': '综合新闻',
                    }
                )

        # --- c) Tabbed news lists (综合新闻, 理工资讯, 媒体理工) ---
        tab_items = response.css('div.tab_pane ul.list_t2 li')
        self.logger.info(f'Tabbed news lists: {len(tab_items)} items')
        for item in tab_items:
            a = item.css('a')
            if not a:
                continue
            link = a.css('::attr(href)').get()
            title = a.css('span.list_text::text').get()
            date_str = a.css('span.date::text').get()
            if link and title:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title.strip(),
                        'date_str': date_str.strip() if date_str else None,
                        'category': '综合新闻',
                    }
                )

        # --- d) Notice sections (ul.list_t li) ---
        notice_items = response.css('ul.list_t li')
        self.logger.info(f'Notice sections: {len(notice_items)} items')
        for item in notice_items:
            link = item.css('a.list_text::attr(href)').get()
            title = item.css('a.list_text::text').get()
            if not title:
                title = item.css('a.list_text::attr(title)').get()
            date_str = item.css('span.date::text').get()
            if link and title:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_article,
                    meta={
                        'title': title.strip(),
                        'date_str': date_str.strip() if date_str else None,
                        'category': '通知公告',
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

        # --- Title: prefer structured hidden metadata, then h2.article_title ---
        page_title = response.css('#NewsArticleTitle::text').get()
        if page_title:
            page_title = page_title.strip()
        if not page_title:
            page_title = response.css('h2.article_title::text').get()
            if page_title:
                page_title = page_title.strip()
        if page_title:
            title = page_title

        # --- Content extraction ---
        content_parts = []

        content_div_selectors = [
            'div.article_content',    # New redesigned site
            'div.TRS_Editor',         # TRS CMS (WHUT uses this)
            'div.article-content',
            'div.content',
            'div.article-body',
            'div.article',
            'div.wp_articlecontent',
            'div#vsb_content',
            'div.text',
            'article',
        ]

        for div_selector in content_div_selectors:
            paragraphs = response.css(f'{div_selector} p')
            if paragraphs:
                for p in paragraphs:
                    p_text = ' '.join(p.css('*::text, ::text').getall())
                    p_text = re.sub(r'\s+', ' ', p_text).strip()
                    if p_text:
                        content_parts.append(p_text)
                if content_parts:
                    break

        content = '\n\n'.join(content_parts) if content_parts else ''

        # Fallback: XPath text extraction
        if not content:
            content_xpath = response.xpath(
                '//div[contains(@class, "article_content")]//text() | '
                '//div[contains(@class, "content")]//text() | '
                '//div[contains(@class, "article")]//text() | '
                '//div[@id="vsb_content"]//text() | '
                '//div[@class="TRS_Editor"]//text()'
            ).getall()
            if content_xpath:
                content = ' '.join([t.strip() for t in content_xpath if t.strip()])
                content = re.sub(r'\s+', ' ', content).strip()

        content = self.clean_html(content)

        # Fallback for image-only posts
        if not content and title:
            img_alts = response.css('div.article_content img::attr(alt), div.TRS_Editor img::attr(alt)').getall()
            if img_alts:
                img_text = '; '.join([alt.strip() for alt in img_alts if alt.strip()])
                content = f"[图片公告] {img_text}" if img_text else f"[图片公告] {title}"
            else:
                content = f"[图片公告] 详见附图"

        # --- Date: prefer structured hidden metadata ---
        pub_day = response.css('#NewsArticlePubDay::text').get()
        if pub_day:
            pub_day = pub_day.strip()
        published_at = self.parse_date(pub_day) if pub_day else None
        if not published_at:
            # Try visible date span (strip label prefix)
            visible_date = response.css('span.date::text').get()
            if visible_date:
                visible_date = re.sub(r'^发布时间[：:]\s*', '', visible_date.strip())
            published_at = self.parse_date(visible_date) if visible_date else None
        if not published_at and date_str:
            published_at = self.parse_date(date_str)

        # --- Author: prefer structured hidden metadata ---
        author = response.css('#NewsArticleAuthor::text').get()
        if author:
            author = author.strip() or None
        if not author:
            author = response.css('span.author::text, div.author::text').get()
        if not author:
            author_match = re.search(r'(作者|撰稿|编辑)[：:]\s*([^\s\u3000]+)', response.text)
            if author_match:
                author = author_match.group(2)

        # --- Publisher: prefer structured hidden metadata ---
        publisher = response.css('#NewsArticleSource::text').get()
        if publisher:
            publisher = publisher.strip() or None
        if not publisher:
            source_text = response.css('span.source::text').get()
            if source_text:
                publisher = re.sub(r'^信息来源[：:]\s*', '', source_text.strip()) or None
        if not publisher:
            publisher_match = re.search(r'(来源|发布单位|供稿|单位|发布部门|发布者)[：:]\s*([^\s\u3000\|]+)', response.text)
            if publisher_match:
                publisher = publisher_match.group(2).strip()
        if not publisher:
            publisher = response.css('div.source::text, span.publisher::text').get()
        if not publisher:
            meta_section = response.css('div.xl-tie p, div.article-meta').getall()
            for meta_html in meta_section:
                pub_match = re.search(r'(来源|发布单位|供稿)[：:]([^<\s]+)', meta_html)
                if pub_match:
                    publisher = pub_match.group(2).strip()
                    break

        # --- Images ---
        images = response.css(
            'div.article_content img::attr(src), '
            'div.TRS_Editor img::attr(src), '
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
        for link in attachment_links[:10]:
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
                publisher=publisher.strip() if publisher else None,
                images=images,
                attachments=attachments,
                category=category,
                department=department,
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

        # Extract department/college links from sidebar (new selector)
        dept_links = response.css('ul.side_menu_style3 li a::attr(href)').getall()
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
        Extract news items from a category/department list page (redesigned site)
        """
        news_items = response.css('ul.list_t li')

        self.logger.info(f'Found {len(news_items)} news items on {response.url}')

        category = self.extract_category(response.url)

        for item in news_items:
            # Title: use title attribute for full (non-truncated) text
            link = item.css('a.list_text::attr(href)').get()
            title = item.css('a.list_text::attr(title)').get()
            if not title:
                title = item.css('a.list_text::text').get()

            # Date
            date_str = item.css('span.date::text').get()

            # Department tag (e.g. 研究生院)
            dept_tag = item.css('span.list_tag a::text').get()

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
        count_match = re.search(r'var countPage = (\d+);', response.text)
        current_match = re.search(r'var currentPage = (\d+);', response.text)

        if count_match and current_match:
            total_pages = int(count_match.group(1))
            current_page = int(current_match.group(1))

            self.logger.info(f'Pagination: page {current_page + 1}/{total_pages}')

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
                        callback=self.parse_category if any(cat in response.url for cat in ['/xxtg/', '/bmxw/', '/xytg/', '/lgjz/']) else self.parse_department,
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
        elif '/lgjz/' in url:
            return '学术讲座·报告·论坛'
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

            # Format 4: "11-28" or "02-14" (assume current year)
            match = re.search(r'(\d{1,2})-(\d{1,2})', date_str)
            if match:
                month, day = match.groups()
                year = datetime.now().year
                return datetime(year, int(month), int(day)).isoformat()

        except Exception as e:
            self.logger.warning(f'Failed to parse date: {date_str}, error: {e}')

        return None
