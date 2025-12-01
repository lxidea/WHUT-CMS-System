#!/usr/bin/env python3
"""
CMS-WHUT Spider Monitoring Dashboard
Shows real-time status of automated scraping system
"""
import os
import sys
import requests
from datetime import datetime
from tasks import app

# Add spider directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_celery_stats():
    """Get statistics from Celery"""
    inspector = app.control.inspect()

    stats = {
        'active_tasks': inspector.active(),
        'scheduled_tasks': inspector.scheduled(),
        'registered_tasks': inspector.registered(),
    }

    return stats

def get_backend_stats():
    """Get statistics from backend API"""
    try:
        backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000')
        response = requests.get(f"{backend_url}/api/news/", params={'limit': 1}, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                'total_news': data.get('total', 0),
                'status': 'online'
            }
        else:
            return {'status': 'error', 'code': response.status_code}
    except requests.exceptions.RequestException as e:
        return {'status': 'offline', 'error': str(e)}

def get_database_stats():
    """Get database statistics"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            database='cms_whut',
            user='cms_user',
            password='cms_password'
        )
        cursor = conn.cursor()

        # Get total news count
        cursor.execute("SELECT COUNT(*) FROM news")
        total = cursor.fetchone()[0]

        # Get category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM news
            GROUP BY category
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()

        # Get image-only count
        cursor.execute("SELECT COUNT(*) FROM news WHERE content LIKE '[图片公告]%'")
        image_only = cursor.fetchone()[0]

        # Get recent news
        cursor.execute("""
            SELECT title, created_at
            FROM news
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            'total': total,
            'categories': categories,
            'image_only': image_only,
            'recent': recent,
            'status': 'connected'
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def print_dashboard():
    """Print monitoring dashboard"""
    print("\n" + "="*60)
    print("  CMS-WHUT Spider Monitoring Dashboard")
    print("="*60 + "\n")

    # Celery Status
    print("📊 Celery Status")
    print("-" * 60)
    celery_stats = get_celery_stats()

    if celery_stats['active_tasks']:
        active_count = sum(len(tasks) for tasks in celery_stats['active_tasks'].values())
        print(f"  Active Tasks: {active_count}")
    else:
        print("  Active Tasks: 0 (idle)")

    if celery_stats['registered_tasks']:
        for worker, tasks in celery_stats['registered_tasks'].items():
            print(f"  Worker {worker}: {len(tasks)} registered tasks")

    # Backend Status
    print("\n🌐 Backend API Status")
    print("-" * 60)
    backend_stats = get_backend_stats()
    print(f"  Status: {backend_stats.get('status', 'unknown').upper()}")
    if backend_stats.get('total_news'):
        print(f"  Total News in API: {backend_stats['total_news']}")

    # Database Status
    print("\n💾 Database Status")
    print("-" * 60)
    db_stats = get_database_stats()

    if db_stats['status'] == 'connected':
        print(f"  Status: CONNECTED")
        print(f"  Total Articles: {db_stats['total']}")
        print(f"  Image-Only Posts: {db_stats['image_only']}")
        print(f"\n  Category Breakdown:")
        for category, count in db_stats['categories']:
            print(f"    • {category}: {count}")

        print(f"\n  Recent Articles:")
        for title, created_at in db_stats['recent']:
            print(f"    • {title[:50]}... ({created_at.strftime('%Y-%m-%d %H:%M')})")
    else:
        print(f"  Status: {db_stats['status'].upper()}")
        if 'error' in db_stats:
            print(f"  Error: {db_stats['error']}")

    print("\n" + "="*60)
    print(f"  Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        print_dashboard()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
