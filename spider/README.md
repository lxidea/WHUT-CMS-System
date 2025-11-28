# Spider Component

Scrapy-based web scraper for fetching news from Wuhan University of Technology website.

## Features

- Scrapy spider framework for robust crawling
- Automatic content deduplication using content hashing
- Celery integration for scheduled crawling
- Direct API integration with backend
- Polite crawling with rate limiting
- User agent rotation
- HTTP caching

## Project Structure

```
spider/
├── whut_spider/
│   ├── spiders/
│   │   └── whut_news.py      # Main news spider (CUSTOMIZE THIS)
│   ├── items.py               # Data structures
│   ├── middlewares.py         # Spider middlewares
│   ├── pipelines.py           # Data processing pipelines
│   └── settings.py            # Scrapy configuration
├── tasks.py                   # Celery periodic tasks
├── scrapy.cfg                 # Scrapy project config
├── requirements.txt
└── Dockerfile
```

## Important: Customization Required

The spider template at `whut_spider/spiders/whut_news.py` contains **placeholder selectors** that you MUST customize based on your university's actual website structure.

### Steps to Customize:

1. **Inspect the website:**
   - Open your university's news page in a browser
   - Use DevTools (F12) to inspect HTML elements
   - Identify CSS selectors or XPath for:
     - News list links
     - Article title
     - Article content
     - Publish date
     - Author
     - Images
     - Category

2. **Update selectors in `whut_news.py`:**
   ```python
   # Example: Replace this
   title = response.css('h1.article-title::text').get()

   # With your actual selector
   title = response.css('div.content h2::text').get()
   ```

3. **Update start URLs:**
   ```python
   start_urls = [
       'https://actual-news-url.whut.edu.cn/news/',
   ]
   ```

4. **Adjust date parsing:**
   - Update `parse_date()` method to match your site's date format

## Manual Spider Execution

Run spider manually (for testing):
```bash
cd spider
scrapy crawl whut_news
```

With custom settings:
```bash
scrapy crawl whut_news -s DOWNLOAD_DELAY=3
```

## Scheduled Execution with Celery

The spider runs automatically every hour via Celery Beat.

**Start Celery worker:**
```bash
celery -A tasks worker --loglevel=info
```

**Start Celery beat (scheduler):**
```bash
celery -A tasks beat --loglevel=info
```

**Test Celery task manually:**
```bash
python -c "from tasks import test_task; print(test_task.delay().get())"
```

## Schedule Configuration

Edit `tasks.py` to change crawl frequency:

```python
app.conf.beat_schedule = {
    'crawl-whut-news-every-hour': {
        'task': 'tasks.crawl_whut_news',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
    },
}
```

Common schedules:
- Every hour: `crontab(minute=0)`
- Every 6 hours: `crontab(minute=0, hour='*/6')`
- Daily at 8 AM: `crontab(minute=0, hour=8)`
- Every 30 minutes: `crontab(minute='*/30')`

## Development Workflow

1. **Test spider locally:**
   ```bash
   scrapy crawl whut_news -o output.json
   ```

2. **Check scraped data:**
   ```bash
   cat output.json | jq '.[0]'
   ```

3. **View logs:**
   ```bash
   tail -f logs/scrapy.log
   ```

## Pipeline Flow

```
Spider → ContentHashPipeline → BackendAPIPipeline → Database
         (generates hash)       (sends to API)
```

## Configuration

Key settings in `whut_spider/settings.py`:

- `DOWNLOAD_DELAY`: Delay between requests (seconds)
- `CONCURRENT_REQUESTS`: Max parallel requests
- `ROBOTSTXT_OBEY`: Respect robots.txt
- `HTTPCACHE_ENABLED`: Cache HTTP responses

## Adding More Spiders

To scrape multiple sources:

1. Create new spider file:
   ```bash
   cd whut_spider/spiders
   # Copy template
   cp whut_news.py whut_announcements.py
   ```

2. Customize new spider

3. Add to Celery schedule in `tasks.py`

## Troubleshooting

**Spider not finding content:**
- Verify selectors using `scrapy shell <url>`
- Check if site uses JavaScript rendering (may need Playwright)

**Duplicate items:**
- Check content_hash generation
- Verify API deduplication is working

**Rate limiting:**
- Increase `DOWNLOAD_DELAY`
- Reduce `CONCURRENT_REQUESTS`

**Celery not running tasks:**
- Check Redis connection
- Verify celery worker and beat are both running
- Check timezone settings
