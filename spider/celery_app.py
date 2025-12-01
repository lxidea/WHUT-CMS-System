"""
Celery application for CMS-WHUT Spider
Handles automated news scraping with scheduled tasks
"""
from celery import Celery
from celery.schedules import crontab
import os

# Configure Celery app
app = Celery(
    'cms_whut_spider',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks']
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    result_expires=3600,  # Results expire after 1 hour
)

# Periodic task schedule
app.conf.beat_schedule = {
    'scrape-whut-news-hourly': {
        'task': 'tasks.scrape_whut_news',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        # 'schedule': 300.0,  # Every 5 minutes for testing
    },
    'cleanup-old-news-daily': {
        'task': 'tasks.cleanup_old_news',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

if __name__ == '__main__':
    app.start()
