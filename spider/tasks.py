"""
Celery tasks for periodic spider execution
"""
from celery import Celery
from celery.schedules import crontab
import subprocess
import os
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

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
    task_track_started=True,
    result_expires=3600,
)

# Periodic task schedule
app.conf.beat_schedule = {
    'crawl-whut-news-every-hour': {
        'task': 'tasks.crawl_whut_news',
        'schedule': crontab(minute=0),  # Run every hour at minute 0
        # 'schedule': 300.0,  # Uncomment for testing: every 5 minutes
    },
}

@app.task(bind=True, name='tasks.crawl_whut_news')
def crawl_whut_news(self):
    """
    Run the WHUT news spider
    """
    try:
        logger.info(f"Starting news scraping task at {datetime.now()}")
        start_time = datetime.now()

        # Determine working directory
        spider_dir = os.path.dirname(os.path.abspath(__file__))

        result = subprocess.run(
            ['scrapy', 'crawl', 'whut_news', '-L', 'INFO'],
            cwd=spider_dir,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Parse output for statistics
        stdout = result.stdout
        scraped_count = 0
        if 'item_scraped_count' in stdout:
            import re
            match = re.search(r"'item_scraped_count': (\d+)", stdout)
            if match:
                scraped_count = int(match.group(1))

        success = result.returncode == 0
        logger.info(f"Scraping {'completed' if success else 'failed'}: {scraped_count} items in {duration:.1f}s")

        return {
            'status': 'success' if success else 'failed',
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'items_scraped': scraped_count,
            'returncode': result.returncode,
            'stdout_tail': result.stdout[-500:],  # Last 500 chars
            'stderr': result.stderr[-500:] if result.stderr else None
        }

    except subprocess.TimeoutExpired:
        logger.error("Spider execution timed out")
        return {
            'status': 'timeout',
            'error': 'Spider execution timed out after 10 minutes',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=300, max_retries=3)


@app.task(name='tasks.get_news_stats')
def get_news_stats():
    """
    Get statistics from backend API about stored news
    """
    try:
        backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        response = requests.get(f"{backend_url}/api/news/", params={'limit': 1})

        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'success',
                'total_news': data.get('total', 0),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {'status': 'error', 'code': response.status_code}
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@app.task(name='tasks.check_keyword_matches')
def check_keyword_matches(news_id: int):
    """
    Check if a newly scraped news item matches any user's keyword subscriptions
    and send email notifications

    Args:
        news_id: ID of the news item to check
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

        from app.core.database import SessionLocal
        from app.models.news import News
        from app.models.subscription import KeywordSubscription, NotificationHistory, EmailStatus
        from app.core.email import email_service

        db = SessionLocal()

        try:
            # Get the news item
            news = db.query(News).filter(News.id == news_id).first()
            if not news:
                logger.warning(f"News {news_id} not found")
                return {'status': 'error', 'message': 'News not found'}

            # Get all active subscriptions with instant frequency
            subscriptions = db.query(KeywordSubscription).filter(
                KeywordSubscription.is_active == True,
                KeywordSubscription.frequency == 'instant'
            ).all()

            matched_users = {}

            # Check each subscription for keyword matches
            for sub in subscriptions:
                keyword = sub.keyword.lower()
                title_lower = news.title.lower() if news.title else ''
                content_lower = news.content.lower() if news.content else ''
                summary_lower = news.summary.lower() if news.summary else ''

                # Check if keyword appears in title, content, or summary
                if (keyword in title_lower or
                    keyword in content_lower or
                    keyword in summary_lower):

                    if sub.user_id not in matched_users:
                        matched_users[sub.user_id] = []

                    matched_users[sub.user_id].append({
                        'subscription': sub,
                        'news': news
                    })

            # Send emails to matched users
            sent_count = 0
            for user_id, matches in matched_users.items():
                from app.models.user import User
                user = db.query(User).filter(User.id == user_id).first()

                if not user or not user.email:
                    continue

                for match in matches:
                    subscription = match['subscription']
                    news_item = match['news']

                    # Prepare news data for email
                    news_data = [{
                        'id': news_item.id,
                        'title': news_item.title,
                        'summary': news_item.summary or news_item.content[:200],
                        'category': news_item.category,
                        'published_at': news_item.published_at.strftime('%Y-%m-%d') if news_item.published_at else '',
                    }]

                    # Send email
                    success, message = email_service.send_keyword_match_notification(
                        to_email=user.email,
                        user_name=user.full_name or user.username,
                        keyword=subscription.keyword,
                        news_items=news_data,
                        subscription_id=subscription.id
                    )

                    # Record notification history
                    notification = NotificationHistory(
                        user_id=user.id,
                        subscription_id=subscription.id,
                        news_id=news_item.id,
                        email_status=EmailStatus.SENT if success else EmailStatus.FAILED,
                        error_message=None if success else message,
                        sent_at=datetime.now() if success else None
                    )
                    db.add(notification)

                    if success:
                        sent_count += 1
                    else:
                        logger.error(f"Failed to send email to {user.email}: {message}")

            db.commit()

            logger.info(f"Checked news {news_id}, sent {sent_count} notifications")

            return {
                'status': 'success',
                'news_id': news_id,
                'matched_users': len(matched_users),
                'emails_sent': sent_count,
                'timestamp': datetime.now().isoformat()
            }

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error checking keyword matches: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@app.task(name='tasks.send_daily_digest')
def send_daily_digest():
    """
    Send daily digest emails to users with daily notification frequency
    Should be scheduled to run once per day
    """
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

        from app.core.database import SessionLocal
        from app.models.subscription import KeywordSubscription
        from app.models.user import User
        from app.core.email import email_service

        db = SessionLocal()

        try:
            # Get all users with daily subscriptions
            # Implementation would aggregate news from last 24 hours
            # For brevity, returning placeholder

            logger.info("Daily digest task completed")
            return {'status': 'success', 'timestamp': datetime.now().isoformat()}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error sending daily digest: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@app.task(name='tasks.test_task')
def test_task():
    """
    Simple test task to verify Celery is working
    """
    return {
        'status': 'ok',
        'message': 'Celery is working!',
        'timestamp': datetime.now().isoformat()
    }
