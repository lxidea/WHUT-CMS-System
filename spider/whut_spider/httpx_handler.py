"""
Custom HTTPX download handler with SOCKS5 proxy support for Scrapy
"""
import httpx
from scrapy.http import HtmlResponse, Request
from twisted.internet import defer, threads


class HttpxDownloadHandler:
    """
    Custom Scrapy download handler using HTTPX with SOCKS5 proxy support
    """

    def __init__(self, settings):
        self.proxy = settings.get('PROXY')
        self.timeout = settings.getfloat('DOWNLOAD_TIMEOUT', 180)

        # Create a shared httpx client with proxy
        proxy_config = {self.proxy: None} if self.proxy else None
        self.client = httpx.Client(
            proxies=proxy_config,
            timeout=self.timeout,
            follow_redirects=True,
            verify=False  # Disable SSL verification for development
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def download_request(self, request: Request, spider):
        """Download a request using HTTPX"""
        return threads.deferToThread(self._download, request, spider)

    def _download(self, request: Request, spider):
        """Synchronous download method"""
        try:
            # Prepare headers
            headers = dict(request.headers.to_unicode_dict())

            # Make the request
            response = self.client.request(
                method=request.method,
                url=request.url,
                headers=headers,
                content=request.body if request.method != 'GET' else None,
            )

            # Convert httpx response to Scrapy response
            return HtmlResponse(
                url=str(response.url),
                status=response.status_code,
                headers=response.headers,
                body=response.content,
                encoding=response.encoding or 'utf-8',
                request=request,
            )

        except Exception as e:
            spider.logger.error(f'Error downloading {request.url}: {e}')
            raise

    def close(self):
        """Close the HTTPX client"""
        if hasattr(self, 'client'):
            self.client.close()
