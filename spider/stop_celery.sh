#!/bin/bash
# Stop Celery worker and beat scheduler

echo "Stopping Celery services..."

# Stop worker
if [ -f /tmp/celery_worker.pid ]; then
    kill $(cat /tmp/celery_worker.pid) 2>/dev/null
    rm /tmp/celery_worker.pid
    echo "Celery worker stopped"
else
    # Fallback: kill by name
    pkill -f "celery.*worker"
    echo "Celery worker stopped (fallback method)"
fi

# Stop beat
if [ -f /tmp/celery_beat.pid ]; then
    kill $(cat /tmp/celery_beat.pid) 2>/dev/null
    rm /tmp/celery_beat.pid
    echo "Celery beat stopped"
else
    # Fallback: kill by name
    pkill -f "celery.*beat"
    echo "Celery beat stopped (fallback method)"
fi

echo "Celery services stopped!"
