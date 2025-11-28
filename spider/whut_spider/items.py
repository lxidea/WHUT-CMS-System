import scrapy

class NewsItem(scrapy.Item):
    """News item scraped from university website"""
    title = scrapy.Field()
    content = scrapy.Field()
    summary = scrapy.Field()
    source_url = scrapy.Field()
    source_name = scrapy.Field()
    published_at = scrapy.Field()
    author = scrapy.Field()
    images = scrapy.Field()
    attachments = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    content_hash = scrapy.Field()
