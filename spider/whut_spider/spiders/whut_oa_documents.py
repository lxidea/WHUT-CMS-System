import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re
import hashlib
from html import unescape
import json


class WhutOADocumentsSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology OA Public Documents
    (http://oapub.whut.edu.cn:8080/seeyon-pub/article/)

    Categories:
    - dwwj_list - 党委文件 (Party Committee Documents)
    - xzwj_list - 行政文件 (Administrative Documents)
    - jwwj_list - 教务文件 (Academic Affairs Documents)
    - ldjh_list - 领导讲话 (Leadership Speeches)
    - hyjy_list - 会议纪要 (Meeting Minutes)

    Note: This spider requires access to the university internal network (VPN).
    The Seeyon OA system typically uses AJAX/JSON for data loading.
    """
    name = 'whut_oa_documents'
    allowed_domains = ['oapub.whut.edu.cn']

    # Category mappings
    CATEGORIES = {
        'dwwj_list': '党委文件',
        'xzwj_list': '行政文件',
        'jwwj_list': '教务文件',
        'ldjh_list': '领导讲话',
        'hyjy_list': '会议纪要',
    }

    # Base URL for the OA system
    base_url = 'http://oapub.whut.edu.cn:8080/seeyon-pub/article'

    start_urls = [
        'http://oapub.whut.edu.cn:8080/seeyon-pub/article/dwwj_list',
        'http://oapub.whut.edu.cn:8080/seeyon-pub/article/xzwj_list',
        'http://oapub.whut.edu.cn:8080/seeyon-pub/article/jwwj_list',
        'http://oapub.whut.edu.cn:8080/seeyon-pub/article/ldjh_list',
        'http://oapub.whut.edu.cn:8080/seeyon-pub/article/hyjy_list',
    ]

    # Track visited URLs
    visited_urls = set()

    # Maximum pages per category
    max_pages_per_category = 5

    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # Be gentle with the OA server
        'DOWNLOAD_TIMEOUT': 30,  # Increase timeout for slow responses
        'ROBOTSTXT_OBEY': False,  # OA systems often don't have robots.txt
        'RETRY_TIMES': 2,  # Retry failed requests
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    def parse(self, response):
        """
        Parse category list page - Seeyon OA specific implementation
        """
        # Determine category from URL
        category = self.get_category_from_url(response.url)
        cat_code = self.get_cat_code_from_url(response.url)

        self.logger.info(f'Parsing OA category "{category}": {response.url}')

        # Seeyon OA uses JavaScript:OpenNewWindow('id') pattern
        # Extract document IDs from these JavaScript calls
        yield from self.parse_seeyon_table(response, category, cat_code)

    def parse_seeyon_table(self, response, category, cat_code):
        """
        Parse Seeyon OA table layout with JavaScript:OpenNewWindow('id') pattern

        HTML structure:
        <table class="list">
            <tr class="Head">...</tr>  <!-- header row -->
            <tr>
                <td class="t_icon">...</td>
                <td nowrap><a href="JavaScript:OpenNewWindow('id')">title</a></td>
                <td>department</td>
                <td>...</td>
                <td>date</td>
            </tr>
        </table>
        """
        item_count = 0

        # Get the detail URL pattern from the category code
        # e.g., xzwj_list -> xzwj_detail
        detail_type = cat_code.replace('_list', '_detail')

        # Find all table rows (skip header rows with class "Head")
        rows = response.css('table.list tr:not(.Head)')

        for row in rows:
            cells = row.css('td')
            if len(cells) < 3:
                continue

            # Extract the JavaScript onclick to get document ID
            # The link is in the second cell (index 1)
            link_elem = row.css('a[href*="OpenNewWindow"]').get()
            if not link_elem:
                continue

            # Get all links in row to find the title link (not the "2" link)
            links = row.css('a[href*="OpenNewWindow"]')
            title_link = None
            for link in links:
                text = link.css('::text').get()
                if text and len(text.strip()) > 5:  # Title should be longer than just "2"
                    title_link = link
                    break

            if not title_link:
                continue

            href = title_link.css('::attr(href)').get()
            if not href:
                continue

            # Extract ID from JavaScript:OpenNewWindow('id') - ID can be negative
            id_match = re.search(r"OpenNewWindow\(['\"](-?\d+)['\"]\)", href)
            if not id_match:
                continue

            doc_id = id_match.group(1)

            # Get title (includes document number like 校办字〔2025〕29号)
            title = title_link.css('::text').get()
            if not title:
                continue
            title = title.strip()

            # Skip pagination links
            if title in ['下页', '上页', '首页', '末页', '尾页', '2']:
                continue

            # Extract department (拟文单位) - third cell (index 2)
            department = None
            if len(cells) >= 3:
                dept_cell = cells[2]
                department = dept_cell.css('::text').get()
                if department:
                    department = department.strip()

            # Extract date - last cell with date format
            date_str = None
            for cell in reversed(cells):
                cell_text = cell.css('::text').get()
                if cell_text:
                    cell_text = cell_text.strip()
                    if re.match(r'\d{4}-\d{2}-\d{2}', cell_text):
                        date_str = cell_text
                        break

            # Construct the detail URL
            detail_url = f'{self.base_url}/{detail_type}?id={doc_id}'

            if detail_url not in self.visited_urls:
                self.visited_urls.add(detail_url)
                item_count += 1
                yield scrapy.Request(
                    detail_url,
                    callback=self.parse_document,
                    meta={
                        'title': title,
                        'doc_id': doc_id,
                        'date_str': date_str,
                        'department': department,
                        'category': category
                    }
                )

        self.logger.info(f'Found {item_count} documents for {category}')

        # Handle pagination - look for page links
        page_links = response.css('a[href*="page="]::attr(href)').getall()
        for page_link in page_links:
            full_url = response.urljoin(page_link)
            if full_url not in self.visited_urls:
                # Check if this is within page limit
                page_match = re.search(r'page=(\d+)', page_link)
                if page_match:
                    page_num = int(page_match.group(1))
                    if page_num <= self.max_pages_per_category:
                        self.visited_urls.add(full_url)
                        yield scrapy.Request(
                            full_url,
                            callback=self.parse,
                            meta={'category': category}
                        )

    def is_valid_url(self, href):
        """
        Check if a URL is valid and not a JavaScript link
        """
        if not href:
            return False
        href_lower = href.lower().strip()
        if href_lower.startswith('javascript:') or href_lower.startswith('javascript '):
            return False
        if href == '#' or href_lower == 'void(0)':
            return False
        if 'javascript:' in href_lower:
            return False
        return True

    def parse_table_layout(self, response, rows, category, cat_code):
        """
        Parse table-based document list
        """
        item_count = 0

        for row in rows:
            # Skip header rows
            if row.css('th'):
                continue

            # Extract link
            link = row.css('a::attr(href)').get()
            if not self.is_valid_url(link):
                continue

            # Get title
            title = row.css('a::attr(title)').get()
            if not title:
                title = row.css('a::text').get()
            if not title:
                continue

            title = title.strip()

            # Extract document number (发文字号)
            doc_number = None
            cells = row.css('td')
            for cell in cells:
                cell_text = cell.css('::text').get()
                if cell_text:
                    # Look for patterns like 校党字〔2024〕1号
                    doc_match = re.search(
                        r'([校党政办纪教研学团工委]+[〔\[]\d{4}[〕\]]\d+号)',
                        cell_text
                    )
                    if doc_match:
                        doc_number = doc_match.group(1)
                        break

            # Extract date
            date_str = None
            for cell in cells:
                cell_text = cell.css('::text').get()
                if cell_text:
                    date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', cell_text)
                    if date_match:
                        date_str = date_match.group(1)
                        break

            # Extract issuing department
            department = None
            dept_patterns = ['发文单位', '发布单位', '来源']
            for i, cell in enumerate(cells):
                header = row.css(f'th:nth-child({i+1})::text').get()
                if header and any(p in header for p in dept_patterns):
                    department = cell.css('::text').get()
                    if department:
                        department = department.strip()
                    break

            full_url = response.urljoin(link)
            if full_url not in self.visited_urls:
                self.visited_urls.add(full_url)
                item_count += 1
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_document,
                    meta={
                        'title': title,
                        'doc_number': doc_number,
                        'date_str': date_str,
                        'department': department,
                        'category': category
                    }
                )

        self.logger.info(f'Found {item_count} documents in table layout for {category}')

        # Handle pagination
        yield from self.follow_pagination(response, category, cat_code)

    def parse_list_layout(self, response, items, category, cat_code):
        """
        Parse list-based document layout
        """
        item_count = 0

        for item in items:
            link = item.css('a::attr(href)').get()
            if not self.is_valid_url(link):
                continue

            title = item.css('a::attr(title)').get()
            if not title:
                title = item.css('a::text').get()
            if not title:
                continue

            title = title.strip()

            # Extract date
            date_str = item.css('span.date::text, span.time::text').get()
            if not date_str:
                item_text = item.get()
                date_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', item_text)
                if date_match:
                    date_str = date_match.group(1)

            full_url = response.urljoin(link)
            if full_url not in self.visited_urls:
                self.visited_urls.add(full_url)
                item_count += 1
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_document,
                    meta={
                        'title': title,
                        'date_str': date_str,
                        'category': category
                    }
                )

        self.logger.info(f'Found {item_count} documents in list layout for {category}')
        yield from self.follow_pagination(response, category, cat_code)

    def parse_div_layout(self, response, divs, category, cat_code):
        """
        Parse div-based document layout
        """
        item_count = 0

        for div in divs:
            link = div.css('a::attr(href)').get()
            if not self.is_valid_url(link):
                continue

            title = div.css('a::attr(title), h3::text, h4::text, .title::text').get()
            if not title:
                title = div.css('a::text').get()
            if not title:
                continue

            title = title.strip()

            date_str = div.css('.date::text, .time::text, span::text').get()

            full_url = response.urljoin(link)
            if full_url not in self.visited_urls:
                self.visited_urls.add(full_url)
                item_count += 1
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_document,
                    meta={
                        'title': title,
                        'date_str': date_str,
                        'category': category
                    }
                )

        self.logger.info(f'Found {item_count} documents in div layout for {category}')
        yield from self.follow_pagination(response, category, cat_code)

    def parse_generic_layout(self, response, category, cat_code):
        """
        Generic fallback parser - extract all article-like links
        """
        item_count = 0

        # Look for any links that seem to be documents
        all_links = response.css('a')

        for link_elem in all_links:
            href = link_elem.css('::attr(href)').get()
            if not href:
                continue

            # Skip non-document links
            if not self.is_valid_url(href):
                continue
            if 'list' in href.lower():
                continue  # Skip list pages

            # Look for article/detail patterns in URL
            if not any(p in href.lower() for p in ['article', 'detail', 'view', 'content', 'show']):
                continue

            title = link_elem.css('::attr(title)').get()
            if not title:
                title = link_elem.css('::text').get()
            if not title or len(title.strip()) < 5:
                continue

            title = title.strip()

            full_url = response.urljoin(href)
            if full_url not in self.visited_urls:
                self.visited_urls.add(full_url)
                item_count += 1
                yield scrapy.Request(
                    full_url,
                    callback=self.parse_document,
                    meta={
                        'title': title,
                        'category': category
                    }
                )

        self.logger.info(f'Found {item_count} documents in generic layout for {category}')
        yield from self.follow_pagination(response, category, cat_code)

    def follow_pagination(self, response, category, cat_code):
        """
        Handle pagination for document lists
        """
        # Look for createPageHTML pattern (common in Chinese CMS)
        page_match = re.search(r'createPageHTML\((\d+),\s*(\d+)', response.text)
        if page_match:
            total_pages = int(page_match.group(1))
            current_idx = int(page_match.group(2))
            if current_idx + 1 < total_pages and current_idx < self.max_pages_per_category:
                next_idx = current_idx + 1
                if next_idx == 0:
                    next_url = f'{self.base_url}/{cat_code}'
                else:
                    next_url = f'{self.base_url}/{cat_code}_{next_idx}'

                if next_url not in self.visited_urls:
                    self.visited_urls.add(next_url)
                    yield scrapy.Request(
                        next_url,
                        callback=self.parse,
                        meta={'category': category}
                    )
                return

        # Try explicit next link
        next_link = response.css(
            'a.next::attr(href), '
            'a:contains("下一页")::attr(href), '
            'a:contains("»")::attr(href), '
            'a.page-next::attr(href)'
        ).get()

        if next_link and next_link not in self.visited_urls:
            self.visited_urls.add(next_link)
            yield scrapy.Request(
                response.urljoin(next_link),
                callback=self.parse,
                meta={'category': category}
            )

    def parse_document(self, response):
        """
        Parse individual Seeyon OA document page
        The page uses a table-based layout with rows like:
        - 标题 | [title]
        - 分类 | [category] | 拟文人 | [author]
        - 发布时间 | [date] | 拟文单位 | [department]
        - 附件 | [attachments with download links]
        """
        title = response.meta.get('title')
        doc_id = response.meta.get('doc_id')
        date_str = response.meta.get('date_str')
        department = response.meta.get('department')
        category = response.meta.get('category', '行政文件')

        self.logger.info(f'Parsing document: {title[:50] if title else response.url}')

        # Extract info from Seeyon table format
        # Find all table rows with class "bgcolor"
        rows = response.css('tr.bgcolor')

        author = None
        for row in rows:
            cells = row.css('td')
            for i, cell in enumerate(cells):
                cell_text = cell.css('::text').get()
                if not cell_text:
                    continue
                cell_text = cell_text.strip()

                # Get the next cell value
                if i + 1 < len(cells):
                    value_cell = cells[i + 1]
                    value = value_cell.css('::text').get()
                    if value:
                        value = value.strip()

                    if '标' in cell_text and '题' in cell_text and not title:
                        title = value
                    elif '发布时间' in cell_text and not date_str:
                        date_str = value
                    elif '拟文单位' in cell_text and not department:
                        department = value
                    elif '拟文人' in cell_text and not author:
                        author = value

        # Get title from page title if not found
        if not title:
            title = response.css('title::text').get()
            if title:
                # Remove prefix like "学校文件:"
                title = re.sub(r'^[^:：]+[:：]\s*', '', title)
                title = title.strip()

        # Extract attachments - Seeyon uses file download links
        attachments = []
        file_links = response.css('a[href*="/file/file"]')
        for link in file_links:
            href = link.css('::attr(href)').get()
            name = link.css('::text').get()
            if href:
                attachments.append({
                    'name': name.strip() if name else '正文下载',
                    'url': response.urljoin(href)
                })

        # Also check for other attachment patterns
        other_attachments = response.css(
            'a[href$=".pdf"], '
            'a[href$=".doc"], '
            'a[href$=".docx"], '
            'a[download]'
        )
        for link in other_attachments:
            href = link.css('::attr(href)').get()
            name = link.css('::text').get() or link.css('::attr(download)').get()
            if href and href not in [a['url'] for a in attachments]:
                attachments.append({
                    'name': name.strip() if name else href.split('/')[-1],
                    'url': response.urljoin(href)
                })

        # For Seeyon OA, the main content is usually in the attachment (正文)
        # Create content from title and metadata
        content_parts = []
        if title:
            content_parts.append(f"标题: {title}")
        if category:
            content_parts.append(f"分类: {category}")
        if department:
            content_parts.append(f"拟文单位: {department}")
        if author:
            content_parts.append(f"拟文人: {author}")
        if date_str:
            content_parts.append(f"发布时间: {date_str}")
        if attachments:
            content_parts.append(f"\n附件: 本文件包含 {len(attachments)} 个附件，请下载查看完整内容。")

        content = '\n'.join(content_parts) if content_parts else ''

        published_at = self.parse_date(date_str) if date_str else None

        # Skip if no title
        if not title:
            self.logger.warning(f'No title found: {response.url}')
            return

        # Generate summary
        summary = content[:200] + '...' if len(content) > 200 else content

        # Generate content hash
        content_hash = hashlib.sha256(f"{title}{content}".encode()).hexdigest()

        # Determine source name based on category
        source_name = f'武汉理工大学OA-{category}'

        yield NewsItem(
            title=self.clean_html(title),
            content=content,
            summary=summary,
            source_url=response.url,
            source_name=source_name,
            published_at=published_at,
            author=author.strip() if author else None,
            publisher=department.strip() if department else None,
            images=[],
            attachments=attachments,
            category=category,
            department=department.strip() if department else None,
            tags=['公文', '文件', category],
            content_hash=content_hash,
        )
        self.logger.info(f'Successfully scraped OA document: {title[:50]}...')

    def get_category_from_url(self, url):
        """
        Extract category name from URL
        """
        for code, name in self.CATEGORIES.items():
            if code in url:
                return name
        return '行政文件'

    def get_cat_code_from_url(self, url):
        """
        Extract category code from URL
        """
        for code in self.CATEGORIES.keys():
            if code in url:
                return code
        return 'xzwj_list'

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

            if re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                return datetime.strptime(date_str[:10], '%Y/%m/%d').isoformat()

            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).isoformat()

        except Exception as e:
            self.logger.warning(f'Failed to parse date: {date_str}, error: {e}')

        return None
