# Scrapy settings for whut_spider project

BOT_NAME = 'whut_spider'

SPIDER_MODULES = ['whut_spider.spiders']
NEWSPIDER_MODULE = 'whut_spider.spiders'

# Crawl responsibly by identifying yourself
USER_AGENT = 'Mozilla/5.0 (compatible; WHUT-CMS-Spider/1.0; +http://cms.whut.edu.cn)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Disabled for campus news crawling

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website (increased for comprehensive crawling)
DOWNLOAD_DELAY = 2  # 2 seconds between requests
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # Reduced to 2 for more respectful crawling

# Disable cookies
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    'whut_spider.middlewares.DuplicateFilterMiddleware': 100,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'whut_spider.middlewares.ProxyMiddleware': 350,
    'whut_spider.middlewares.RandomUserAgentMiddleware': 400,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'whut_spider.pipelines.ContentHashPipeline': 100,
    'whut_spider.pipelines.BackendAPIPipeline': 300,
}

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404]

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

# Custom settings
# For local development, use localhost; for Docker, use service name 'backend'
BACKEND_API_URL = 'http://localhost:8000'

# SOCKS5 Proxy configuration (for off-campus access to WHUT website)
# Disabled - using VPN connection instead
# HTTPPROXY_ENABLED = True
# PROXY = 'socks5://18.tcp.vip.cpolar.cn:14593'

# Custom download handlers (using HTTPX with SOCKS5 support)
# Disabled - using VPN connection with standard Scrapy handlers
# DOWNLOAD_HANDLERS = {
#     'http': 'whut_spider.httpx_handler.HttpxDownloadHandler',
#     'https': 'whut_spider.httpx_handler.HttpxDownloadHandler',
# }
