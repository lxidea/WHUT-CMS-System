import random
from scrapy import signals

class RandomUserAgentMiddleware:
    """Rotate user agents to avoid detection"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.USER_AGENTS)


class DuplicateFilterMiddleware:
    """Filter duplicate items based on URL"""

    def __init__(self):
        self.seen_urls = set()

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info('DuplicateFilterMiddleware enabled')

    def process_spider_output(self, response, result, spider):
        for item in result:
            if hasattr(item, 'get') and 'source_url' in item:
                url = item.get('source_url')
                if url not in self.seen_urls:
                    self.seen_urls.add(url)
                    yield item
                else:
                    spider.logger.debug(f'Duplicate URL filtered: {url}')
            else:
                yield item
