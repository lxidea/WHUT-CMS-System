import scrapy
from datetime import datetime
from whut_spider.items import NewsItem
import re

class WhutNewsSpider(scrapy.Spider):
    """
    Spider for Wuhan University of Technology news website

    This is a template spider - you'll need to customize the selectors
    based on the actual structure of your university's news website.
    """
    name = 'whut_news'
    allowed_domains = ['whut.edu.cn']  # Update with actual domain

    # Example start URLs - update with actual news list pages
    start_urls = [
        'http://www.whut.edu.cn/xw/index.htm',  # Example main news page
        # Add more news category URLs here
    ]

    def parse(self, response):
        """
        Parse news list page and extract article links
        """
        # Example selector - CUSTOMIZE THIS based on actual HTML structure
        news_links = response.css('div.news-list a.news-title::attr(href)').getall()

        for link in news_links:
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_article)

        # Follow pagination if exists
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """
        Parse individual news article page

        IMPORTANT: Customize all CSS/XPath selectors based on your university's
        actual website structure. Use browser DevTools to inspect elements.
        """

        # Extract title - CUSTOMIZE SELECTOR
        title = response.css('h1.article-title::text').get()
        if not title:
            title = response.css('title::text').get()

        # Extract content - CUSTOMIZE SELECTOR
        # Join all paragraphs into single content
        content_parts = response.css('div.article-content p::text').getall()
        content = '\n\n'.join(content_parts) if content_parts else ''

        # Extract publish date - CUSTOMIZE SELECTOR AND FORMAT
        date_str = response.css('span.publish-date::text').get()
        published_at = self.parse_date(date_str) if date_str else None

        # Extract author - CUSTOMIZE SELECTOR
        author = response.css('span.author::text').get()

        # Extract images - CUSTOMIZE SELECTOR
        images = response.css('div.article-content img::attr(src)').getall()
        images = [response.urljoin(img) for img in images]

        # Extract category from breadcrumb or URL - CUSTOMIZE
        category = response.css('div.breadcrumb a:nth-child(2)::text').get()

        # Generate summary from first paragraph or extract if exists
        summary = content_parts[0] if content_parts else None
        if summary and len(summary) > 200:
            summary = summary[:200] + '...'

        # Extract attachments/downloads if any - CUSTOMIZE
        attachments = []
        attachment_links = response.css('div.attachments a')
        for link in attachment_links:
            attachments.append({
                'name': link.css('::text').get(),
                'url': response.urljoin(link.css('::attr(href)').get())
            })

        # Only yield if we have minimum required data
        if title and content:
            yield NewsItem(
                title=title.strip(),
                content=content.strip(),
                summary=summary,
                source_url=response.url,
                source_name='武汉理工大学',  # Wuhan University of Technology
                published_at=published_at,
                author=author.strip() if author else None,
                images=images,
                attachments=attachments,
                category=category.strip() if category else '综合新闻',
                tags=[],  # Can extract tags if available
            )
        else:
            self.logger.warning(f'Incomplete data for URL: {response.url}')

    def parse_date(self, date_str):
        """
        Parse date string to ISO format
        CUSTOMIZE based on your university's date format
        """
        try:
            # Example formats - adjust based on actual format
            # Format 1: "2024-01-15"
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return datetime.strptime(date_str, '%Y-%m-%d').isoformat()

            # Format 2: "2024年01月15日"
            match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
            if match:
                year, month, day = match.groups()
                return datetime(int(year), int(month), int(day)).isoformat()

            # Add more date formats as needed

        except Exception as e:
            self.logger.warning(f'Failed to parse date: {date_str}, error: {e}')

        return None
