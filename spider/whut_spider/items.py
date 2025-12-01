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
    publisher = scrapy.Field()  # Publishing unit (XX学院, XX部)
    images = scrapy.Field()
    attachments = scrapy.Field()
    category = scrapy.Field()
    department = scrapy.Field()  # Department or college name
    tags = scrapy.Field()
    content_hash = scrapy.Field()
