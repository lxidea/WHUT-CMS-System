# Email Notification System - Quick Setup Guide

## ✅ What's Been Implemented

Your CMS-WHUT now has a **complete email notification system** for keyword subscriptions!

### Features Completed:

1. **✅ Database Models**
   - `keyword_subscriptions` table - Stores user keyword subscriptions
   - `notification_history` table - Tracks all sent emails
   - Alembic migration created and applied

2. **✅ Backend API Endpoints**
   - `POST /api/subscriptions/` - Create subscription
   - `POST /api/subscriptions/bulk` - Create multiple subscriptions
   - `GET /api/subscriptions/` - Get user's subscriptions
   - `PATCH /api/subscriptions/{id}` - Update subscription
   - `DELETE /api/subscriptions/{id}` - Delete subscription
   - `POST /api/subscriptions/{id}/unsubscribe` - Unsubscribe (public, for email links)
   - `GET /api/subscriptions/history/` - View notification history

3. **✅ Email Service**
   - Professional HTML email templates with responsive design
   - SMTP configuration support (Gmail, Outlook, SendGrid, AWS SES)
   - Beautiful email design with gradients and cards

4. **✅ Celery Tasks**
   - `check_keyword_matches(news_id)` - Checks if news matches keywords and sends emails
   - Automatically triggered when spider saves new articles
   - Non-blocking, runs in background

5. **✅ Integration with Spider**
   - Spider pipeline automatically triggers keyword matching
   - When new article is saved (HTTP 201), triggers Celery task
   - Finds matching keywords in title, content, and summary

---

## 🚀 Quick Start

### 1. Configure Email Settings

Create/edit `.env` file in backend directory:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password  # NOT your regular password!
FROM_EMAIL=noreply@cms-whut.edu.cn
FROM_NAME=CMS-WHUT 通知系统

# Frontend URL for links
FRONTEND_URL=http://localhost:3000
```

**For Gmail:**
1. Enable 2FA on your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Create an "App Password" for "Mail"
4. Use that 16-character password in `SMTP_PASSWORD`

### 2. Restart Celery Workers

The Celery workers need the new task code:

```bash
cd /home/laixin/projects/cms-whut/spider
./stop_celery.sh
./start_celery.sh
```

### 3. Test the System

**Create a test subscription:**

```bash
# First, get a JWT token by logging in (you'll need to create a user first)
# Then create a subscription:

curl -X POST http://localhost:8000/api/subscriptions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "keyword": "考试",
    "frequency": "instant"
  }'
```

**Manually trigger keyword check:**

```bash
cd /home/laixin/projects/cms-whut/spider
source venv/bin/activate
python3 << 'EOF'
from tasks import check_keyword_matches
# Check news ID 1 for keyword matches
result = check_keyword_matches.delay(1)
print(f"Task triggered: {result.id}")
EOF
```

---

## 📚 How It Works

```
1. User subscribes to keyword "奖学金" via API
   ↓
2. Spider scrapes new article titled "关于2025年奖学金评选通知"
   ↓
3. Article saved to database, returns news_id=100
   ↓
4. Spider pipeline triggers: check_keyword_matches.delay(100)
   ↓
5. Celery worker:
   - Queries all active subscriptions
   - Checks if "奖学金" appears in title/content/summary
   - Finds match!
   ↓
6. Celery worker sends email:
   - Fetches user info
   - Renders HTML email template
   - Sends via SMTP
   ↓
7. Records notification in notification_history table
```

---

## 🧪 Testing Without Email

If you don't want to configure email yet, the system still works:
- API endpoints are fully functional
- Subscriptions are created and stored
- Keyword matching logic runs
- Email sending will fail gracefully (logs warning)
- Notification history records the failure

---

## 📖 Full Documentation

See `/home/laixin/projects/cms-whut/docs/EMAIL_NOTIFICATIONS.md` for:
- Complete API reference
- Email provider configurations
- Database schema details
- Troubleshooting guide
- Advanced features

---

## 🎯 Next Steps

1. **Configure email** (see above)
2. **Restart Celery workers** to load new tasks
3. **Create test user and subscription**
4. **Wait for spider to run** (every hour at minute 0)
5. **Check your email!**

Or manually trigger:
```bash
python3 -c "from tasks import check_keyword_matches; check_keyword_matches.delay(1)"
```

---

## 🐛 Troubleshooting

**Emails not sending?**
- Check `/tmp/celery_worker.log` for errors
- Verify SMTP credentials in `.env`
- Test SMTP connection manually (see docs)

**Keywords not matching?**
- Keywords are case-insensitive
- Matches in title, content, OR summary
- Check notification_history table for results

**Celery tasks not running?**
```bash
cd spider
./status_celery.sh  # Should show worker and beat running
```

---

## ✨ System is Ready!

Your email notification system is fully implemented and ready to use. Just configure your SMTP settings and restart Celery workers!

**API Documentation**: http://localhost:8000/docs (look for "subscriptions" section)
