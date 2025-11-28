"""
Celery tasks for periodic spider execution
"""
from celery import Celery
from celery.schedules import crontab
import subprocess
import os

# Initialize Celery
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app = Celery('whut_spider', broker=redis_url, backend=redis_url)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

# Periodic task schedule
app.conf.beat_schedule = {
    'crawl-whut-news-every-hour': {
        'task': 'tasks.crawl_whut_news',
        'schedule': crontab(minute=0),  # Run every hour
    },
}

@app.task(name='tasks.crawl_whut_news')
def crawl_whut_news():
    """
    Run the WHUT news spider
    """
    try:
        result = subprocess.run(
            ['scrapy', 'crawl', 'whut_news'],
            cwd='/app',
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        return {
            'status': 'success' if result.returncode == 0 else 'failed',
            'returncode': result.returncode,
            'stdout': result.stdout[-1000:],  # Last 1000 chars
            'stderr': result.stderr[-1000:] if result.stderr else None
        }

    except subprocess.TimeoutExpired:
        return {
            'status': 'timeout',
            'error': 'Spider execution timed out after 10 minutes'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

@app.task(name='tasks.test_task')
def test_task():
    """
    Simple test task to verify Celery is working
    """
    return {'status': 'ok', 'message': 'Celery is working!'}
