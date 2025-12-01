#!/bin/bash
# Check status of Celery services

echo "=== Celery Services Status ==="
echo ""

# Check worker
if pgrep -f "celery.*worker" > /dev/null; then
    worker_count=$(pgrep -f "celery.*worker" | wc -l)
    echo "✓ Celery Worker: RUNNING ($worker_count processes)"
else
    echo "✗ Celery Worker: STOPPED"
fi

# Check beat
if pgrep -f "celery.*beat" > /dev/null; then
    echo "✓ Celery Beat: RUNNING"
else
    echo "✗ Celery Beat: STOPPED"
fi

# Check Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis: RUNNING"
else
    echo "✗ Redis: STOPPED"
fi

echo ""
echo "=== Recent Worker Log (last 10 lines) ==="
if [ -f /tmp/celery_worker.log ]; then
    tail -10 /tmp/celery_worker.log
else
    echo "Log file not found"
fi

echo ""
echo "=== Recent Beat Log (last 10 lines) ==="
if [ -f /tmp/celery_beat.log ]; then
    tail -10 /tmp/celery_beat.log
else
    echo "Log file not found"
fi
