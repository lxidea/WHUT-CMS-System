# Email Notification System Documentation

## Overview

The CMS-WHUT email notification system allows users to subscribe to keywords and receive instant email notifications when new articles matching their keywords are published.

## Features

✅ **Keyword Subscriptions**: Users can subscribe to multiple keywords
✅ **Instant Notifications**: Receive emails immediately when matching news is found
✅ **Daily Digest**: Option for daily summary emails (coming soon)
✅ **Notification History**: Track all sent notifications
✅ **Beautiful HTML Emails**: Professional email templates with responsive design
✅ **Unsubscribe Links**: Easy one-click unsubscribe from email

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Spider scrapes new news                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          News saved to database via API                 │
│              (returns news_id)                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│    Celery task: check_keyword_matches(news_id)          │
│    - Query all active subscriptions                     │
│    - Check if keywords match (title/content/summary)    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Send email to matched users                     │
│         Record in notification_history                  │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Email Service Setup

Configure email settings in environment variables or `.env` file:

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com              # SMTP server
SMTP_PORT=587                         # SMTP port (587 for TLS)
SMTP_USER=your-email@gmail.com        # Email account
SMTP_PASSWORD=your-app-password       # App password (not regular password!)
FROM_EMAIL=noreply@cms-whut.edu.cn   # Sender email
FROM_NAME=CMS-WHUT 通知系统            # Sender name

# Frontend URL (for links in emails)
FRONTEND_URL=http://localhost:3000
```

### Gmail Setup

1. Enable 2-Factor Authentication in your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Create an "App Password" for "Mail"
4. Use that 16-character password in `SMTP_PASSWORD`

**Important**: Never use your regular Gmail password!

### Other Email Providers

#### Outlook/Office 365
```bash
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```

#### SendGrid
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<your-sendgrid-api-key>
```

#### AWS SES
```bash
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<your-ses-smtp-username>
SMTP_PASSWORD=<your-ses-smtp-password>
```

---

## API Endpoints

### Create Subscription

**POST** `/api/subscriptions/`

Subscribe to a keyword.

**Request Body:**
```json
{
  "keyword": "奖学金",
  "frequency": "instant"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "user_id": 5,
  "keyword": "奖学金",
  "is_active": true,
  "frequency": "instant",
  "created_at": "2025-11-30T12:00:00Z",
  "updated_at": null
}
```

### Bulk Create Subscriptions

**POST** `/api/subscriptions/bulk`

Subscribe to multiple keywords at once.

**Request Body:**
```json
{
  "keywords": ["考试", "奖学金", "讲座"],
  "frequency": "instant"
}
```

### Get My Subscriptions

**GET** `/api/subscriptions/?page=1&page_size=20&active_only=true`

List current user's subscriptions.

**Response:**
```json
{
  "total": 3,
  "items": [
    {
      "id": 1,
      "user_id": 5,
      "keyword": "奖学金",
      "is_active": true,
      "frequency": "instant",
      "created_at": "2025-11-30T12:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20
}
```

### Update Subscription

**PATCH** `/api/subscriptions/{id}`

Update a subscription (activate/deactivate or change frequency).

**Request Body:**
```json
{
  "is_active": false
}
```

### Delete Subscription

**DELETE** `/api/subscriptions/{id}`

Permanently delete a subscription.

**Response:** `204 No Content`

### Unsubscribe (Public)

**POST** `/api/subscriptions/{id}/unsubscribe`

Unsubscribe from keyword (no authentication required - for email links).

### Get Notification History

**GET** `/api/subscriptions/history/?page=1&page_size=20`

View notification history.

**Response:**
```json
{
  "total": 15,
  "items": [
    {
      "id": 100,
      "user_id": 5,
      "subscription_id": 1,
      "news_id": 200,
      "email_status": "sent",
      "error_message": null,
      "sent_at": "2025-11-30T12:05:00Z",
      "created_at": "2025-11-30T12:05:00Z"
    }
  ],
  "page": 1,
  "page_size": 20
}
```

---

## Database Schema

### keyword_subscriptions

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| keyword | String | Keyword to match (lowercase) |
| is_active | Boolean | Active status |
| frequency | Enum | instant/daily/weekly |
| created_at | DateTime | Created timestamp |
| updated_at | DateTime | Updated timestamp |

### notification_history

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users |
| subscription_id | Integer | Foreign key to subscriptions |
| news_id | Integer | Foreign key to news |
| email_status | Enum | pending/sent/failed |
| error_message | String | Error details if failed |
| sent_at | DateTime | When email was sent |
| created_at | DateTime | Created timestamp |

---

## Email Templates

### Keyword Match Notification

Beautiful HTML email with:
- Header with gradient background
- User's name and keyword
- News cards with:
  - Title
  - Category and publish date
  - Summary (first 150 chars)
  - "View Details" button linking to article
- Footer with:
  - Manage subscriptions link
  - Unsubscribe link
  - Project branding

---

## Testing

### 1. Create a Test Subscription

```bash
curl -X POST http://localhost:8000/api/subscriptions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "keyword": "测试",
    "frequency": "instant"
  }'
```

### 2. Trigger Manual Keyword Check

```python
# In spider directory
from tasks import check_keyword_matches

# Check a specific news item
check_keyword_matches.delay(news_id=1)
```

### 3. View Logs

```bash
# Celery worker logs
tail -f /tmp/celery_worker.log

# Check for email sending
grep "keyword matching" /tmp/celery_worker.log
```

---

## Troubleshooting

### Emails Not Sending

**1. Check SMTP credentials:**
```bash
# Test connection
python3 << EOF
import smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login('your-email@gmail.com', 'your-app-password')
print("SMTP connection successful!")
smtp.quit()
EOF
```

**2. Check Celery worker is running:**
```bash
cd /home/laixin/projects/cms-whut/spider
./status_celery.sh
```

**3. Check notification history for errors:**
```sql
SELECT * FROM notification_history
WHERE email_status = 'failed'
ORDER BY created_at DESC
LIMIT 10;
```

### Keywords Not Matching

**1. Check subscription is active:**
```sql
SELECT * FROM keyword_subscriptions
WHERE user_id = YOUR_USER_ID AND is_active = true;
```

**2. Keyword matching is case-insensitive:**
- Keywords are stored in lowercase
- Matching checks title, content, AND summary

**3. Check Celery task is triggered:**
```bash
# Should see entries when spider runs
grep "Triggered keyword matching" /tmp/celery_worker.log
```

---

## Performance Considerations

- Keyword matching runs asynchronously via Celery
- Does NOT slow down spider scraping
- Email sending is non-blocking
- Failed emails are logged but don't retry (to avoid spam)

---

## Security

✅ Subscription endpoints require authentication
✅ Users can only manage their own subscriptions
✅ Unsubscribe endpoint is public (for email links)
✅ Passwords never stored in plaintext
✅ Email credentials in environment variables

---

## Future Enhancements

- [ ] Daily digest emails (aggregate all matches)
- [ ] Weekly digest option
- [ ] Email templates customization
- [ ] Advanced keyword syntax (regex, boolean operators)
- [ ] Notification preferences (email, SMS, push)
- [ ] A/B testing for email templates
- [ ] Analytics dashboard for open rates

---

## Support

For issues or questions:
- Check logs: `/tmp/celery_worker.log`
- Review notification history via API
- Check SMTP configuration
- Ensure Celery workers are running
