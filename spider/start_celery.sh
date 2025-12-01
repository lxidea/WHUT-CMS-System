#!/bin/bash
# Start Celery worker and beat scheduler for CMS-WHUT

cd /home/laixin/projects/cms-whut/spider
source venv/bin/activate

echo "Starting Celery services..."

# Start Celery worker
celery -A tasks worker --loglevel=info --detach --logfile=/tmp/celery_worker.log --pidfile=/tmp/celery_worker.pid

# Start Celery beat scheduler
celery -A tasks beat --loglevel=info --detach --logfile=/tmp/celery_beat.log --pidfile=/tmp/celery_beat.pid

echo "Celery services started!"
echo "Worker log: /tmp/celery_worker.log"
echo "Beat log: /tmp/celery_beat.log"
echo ""
echo "Check status with: ./status_celery.sh"
echo "Stop services with: ./stop_celery.sh"
