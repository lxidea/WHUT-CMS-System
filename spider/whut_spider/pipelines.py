import hashlib
import httpx
from itemadapter import ItemAdapter

class ContentHashPipeline:
    """Generate content hash for deduplication"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Generate hash from title and content
        content = f"{adapter.get('title', '')}{adapter.get('content', '')}"
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        adapter['content_hash'] = content_hash
        return item


class BackendAPIPipeline:
    """Send scraped items to backend API"""

    def __init__(self, api_url):
        self.api_url = api_url
        self.client = None

    @classmethod
    def from_crawler(cls, crawler):
        api_url = crawler.settings.get('BACKEND_API_URL', 'http://backend:8000')
        return cls(api_url)

    def open_spider(self, spider):
        self.client = httpx.Client(timeout=30.0)
        spider.logger.info(f'BackendAPIPipeline connected to {self.api_url}')

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Convert to dict and prepare for API
        data = {
            'title': adapter.get('title'),
            'content': adapter.get('content'),
            'summary': adapter.get('summary'),
            'source_url': adapter.get('source_url'),
            'source_name': adapter.get('source_name'),
            'published_at': adapter.get('published_at'),
            'author': adapter.get('author'),
            'images': adapter.get('images', []),
            'attachments': adapter.get('attachments', []),
            'category': adapter.get('category'),
            'tags': adapter.get('tags', []),
            'content_hash': adapter.get('content_hash'),
        }

        try:
            response = self.client.post(
                f'{self.api_url}/api/news/',
                json=data
            )

            if response.status_code == 201:
                spider.logger.info(f'Successfully saved: {data["title"][:50]}...')

                # Trigger keyword matching for new items
                try:
                    response_data = response.json()
                    news_id = response_data.get('id')
                    if news_id:
                        # Import and trigger celery task asynchronously
                        from tasks import check_keyword_matches
                        check_keyword_matches.delay(news_id)
                        spider.logger.debug(f'Triggered keyword matching for news ID {news_id}')
                except Exception as task_error:
                    spider.logger.warning(f'Failed to trigger keyword matching: {str(task_error)}')

            elif response.status_code == 409:
                spider.logger.debug(f'Duplicate content skipped: {data["title"][:50]}...')
            else:
                spider.logger.error(
                    f'Failed to save item: {response.status_code} - {response.text}'
                )

        except Exception as e:
            spider.logger.error(f'Error sending item to API: {str(e)}')

        return item
