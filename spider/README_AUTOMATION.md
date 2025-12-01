# CMS-WHUT Spider Automation

## Overview

The spider now runs automatically with Celery for scheduled news scraping.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ Celery Beat │────>│ Redis Broker │────>│   Celery   │
│  Scheduler  │     │   (Queue)    │     │   Worker   │
└─────────────┘     └──────────────┘     └────────────┘
                                                 │
                                                 ▼
                                          ┌────────────┐
                                          │   Scrapy   │
                                          │   Spider   │
                                          └────────────┘
                                                 │
                                                 ▼
                                          ┌────────────┐
                                          │  Backend   │
                                          │    API     │
                                          └────────────┘
                                                 │
                                                 ▼
                                          ┌────────────┐
                                          │ PostgreSQL │
                                          │  Database  │
                                          └────────────┘
```

## Components

### 1. Celery Worker
- Executes scraping tasks
- 17 concurrent worker processes
- Auto-retry on failures (max 3 attempts)
- 10-minute timeout per task

### 2. Celery Beat
- Schedules periodic tasks
- Runs scraping every hour (at minute 0)
- Configurable schedule in `tasks.py`

### 3. Redis
- Message broker between Beat and Worker
- Stores task results (1-hour expiration)

## Usage

### Start Services

```bash
cd /home/laixin/projects/cms-whut/spider
./start_celery.sh
```

### Stop Services

```bash
./stop_celery.sh
```

### Check Status

```bash
./status_celery.sh
```

### Monitor Dashboard

```bash
source venv/bin/activate
python3 monitor.py
```

### Manual Task Execution

```python
from tasks import crawl_whut_news, get_news_stats

# Trigger scraping manually
result = crawl_whut_news.delay()
print(f"Task ID: {result.id}")

# Get result
task_result = result.get(timeout=600)
print(task_result)

# Get statistics
stats = get_news_stats.delay().get()
print(stats)
```

## Schedule Configuration

Edit `tasks.py` to modify the schedule:

```python
app.conf.beat_schedule = {
    'crawl-whut-news-every-hour': {
        'task': 'tasks.crawl_whut_news',
        'schedule': crontab(minute=0),  # Every hour
        # 'schedule': crontab(hour=0, minute=0),  # Daily at midnight
        # 'schedule': 300.0,  # Every 5 minutes (for testing)
    },
}
```

## Task Details

### `crawl_whut_news`
- **Schedule**: Every hour at minute 0
- **Timeout**: 10 minutes
- **Retries**: 3 attempts with 5-minute delay
- **Returns**:
  - status: success/failed/timeout
  - timestamp: completion time
  - duration_seconds: execution time
  - items_scraped: number of articles
  - returncode: spider exit code

### `get_news_stats`
- **Type**: On-demand
- **Purpose**: Get backend statistics
- **Returns**: Total news count and status

## Logs

- **Worker Log**: `/tmp/celery_worker.log`
- **Beat Log**: `/tmp/celery_beat.log`

View real-time logs:
```bash
tail -f /tmp/celery_worker.log
tail -f /tmp/celery_beat.log
```

## Performance

- **Scraping Time**: ~5-6 seconds per run
- **Success Rate**: 100% (94/94 items)
- **Full Text**: 80% (74 articles)
- **Image Posts**: 20% (18 posts with placeholders)

## Monitoring

The monitoring dashboard shows:
- ✅ Active/idle tasks
- ✅ Worker status
- ✅ Backend API connectivity
- ✅ Database statistics
- ✅ Category breakdown
- ✅ Recent articles

## Troubleshooting

### Worker Not Starting
```bash
# Check Redis
redis-cli ping

# Check worker logs
tail -100 /tmp/celery_worker.log

# Restart services
./stop_celery.sh && ./start_celery.sh
```

### Tasks Not Executing
```bash
# Verify Beat is running
ps aux | grep "celery.*beat"

# Check Beat logs
tail -100 /tmp/celery_beat.log

# Verify task registration
python3 -c "from tasks import app; print(list(app.tasks.keys()))"
```

### Database Issues
```bash
# Check database connection
PGPASSWORD=cms_password psql -h localhost -U cms_user -d cms_whut -c "SELECT COUNT(*) FROM news;"

# Check backend API
curl http://localhost:8000/api/health
```

## Production Deployment

### 1. Systemd Service

Create `/etc/systemd/system/celery-worker.service`:
```ini
[Unit]
Description=Celery Worker for CMS-WHUT
After=network.target redis.service

[Service]
Type=forking
User=laixin
WorkingDirectory=/home/laixin/projects/cms-whut/spider
ExecStart=/home/laixin/projects/cms-whut/spider/venv/bin/celery -A tasks worker --loglevel=info --detach --pidfile=/tmp/celery_worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/celery-beat.service`:
```ini
[Unit]
Description=Celery Beat for CMS-WHUT
After=network.target redis.service

[Service]
Type=forking
User=laixin
WorkingDirectory=/home/laixin/projects/cms-whut/spider
ExecStart=/home/laixin/projects/cms-whut/spider/venv/bin/celery -A tasks beat --loglevel=info --detach --pidfile=/tmp/celery_beat.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable celery-worker celery-beat
sudo systemctl start celery-worker celery-beat
```

### 2. Monitoring (Optional)

Use Flower for web-based monitoring:
```bash
pip install flower
celery -A tasks flower --port=5555
```

Access at http://localhost:5555

## Next Steps

- [ ] Deploy to production server
- [ ] Add email notifications on failures
- [ ] Implement cleanup task for old news
- [ ] Add performance metrics collection
- [ ] Build frontend dashboard
