from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os
from pathlib import Path
from jinja2 import Template


class EmailService:
    """Email service for sending notifications"""

    def __init__(self):
        # Email configuration from environment variables
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "CMS-WHUT 通知系统")

        # Base URL for links in emails
        self.base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None
    ) -> tuple[bool, str]:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional, falls back to stripped HTML)

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = formataddr((self.from_name, self.from_email))
            msg['To'] = to_email

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)

            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True, "Email sent successfully"

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(error_msg)
            return False, error_msg

    def send_keyword_match_notification(
        self,
        to_email: str,
        user_name: str,
        keyword: str,
        news_items: List[dict],
        subscription_id: int
    ) -> tuple[bool, str]:
        """
        Send notification when news matches user's keyword

        Args:
            to_email: User's email address
            user_name: User's name
            keyword: The matched keyword
            news_items: List of news items (dict with title, summary, url, published_at, category)
            subscription_id: Subscription ID for unsubscribe link

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Load HTML template
        template_path = Path(__file__).parent.parent / "templates" / "keyword_notification.html"

        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_str = f.read()
        else:
            # Fallback inline template
            template_str = self._get_default_notification_template()

        template = Template(template_str)

        # Render template
        html_content = template.render(
            user_name=user_name,
            keyword=keyword,
            news_items=news_items,
            news_count=len(news_items),
            base_url=self.base_url,
            subscription_id=subscription_id
        )

        # Create plain text version
        text_content = f"""
您好 {user_name}，

您订阅的关键词 "{keyword}" 有 {len(news_items)} 条新闻更新：

"""
        for news in news_items:
            text_content += f"\n【{news['category']}】{news['title']}\n"
            text_content += f"{news['summary'][:100]}...\n"
            text_content += f"查看详情: {self.base_url}/news/{news['id']}\n"

        text_content += f"\n\n取消订阅: {self.base_url}/subscriptions/{subscription_id}/unsubscribe"

        subject = f"[CMS-WHUT] 关键词提醒：{keyword} ({len(news_items)}条新消息)"

        return self.send_email(to_email, subject, html_content, text_content)

    def send_daily_digest(
        self,
        to_email: str,
        user_name: str,
        keyword_matches: dict
    ) -> tuple[bool, str]:
        """
        Send daily digest of all matched keywords

        Args:
            to_email: User's email address
            user_name: User's name
            keyword_matches: Dict of {keyword: [news_items]}

        Returns:
            Tuple of (success: bool, message: str)
        """
        total_count = sum(len(items) for items in keyword_matches.values())

        if total_count == 0:
            return True, "No news to send"

        # Similar implementation as keyword notification but with multiple keywords
        # For brevity, using simplified version
        subject = f"[CMS-WHUT] 每日摘要 ({total_count}条新消息)"

        html_content = f"<h2>您好 {user_name}，</h2><p>今日共有 {total_count} 条新闻匹配您的订阅。</p>"

        return self.send_email(to_email, subject, html_content)

    def _get_default_notification_template(self) -> str:
        """Get default HTML email template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }
        .content { background: #f9fafb; padding: 30px; }
        .news-item { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }
        .news-title { font-size: 18px; font-weight: bold; color: #1f2937; margin-bottom: 10px; }
        .news-meta { font-size: 12px; color: #6b7280; margin-bottom: 10px; }
        .news-summary { color: #4b5563; margin-bottom: 15px; }
        .btn { display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }
        .footer { background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 10px 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">🔔 关键词提醒</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">您订阅的关键词有新内容更新</p>
        </div>

        <div class="content">
            <p>您好 <strong>{{ user_name }}</strong>，</p>
            <p>您订阅的关键词 <strong>"{{ keyword }}"</strong> 有 <strong>{{ news_count }}</strong> 条新闻更新：</p>

            {% for news in news_items %}
            <div class="news-item">
                <div class="news-title">{{ news.title }}</div>
                <div class="news-meta">
                    <span>📁 {{ news.category }}</span> |
                    <span>📅 {{ news.published_at }}</span>
                </div>
                <div class="news-summary">{{ news.summary[:150] }}...</div>
                <a href="{{ base_url }}/news/{{ news.id }}" class="btn">查看详情 →</a>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>这是一封自动发送的邮件，请勿回复。</p>
            <p><a href="{{ base_url }}/subscriptions" style="color: #667eea;">管理订阅</a> | <a href="{{ base_url }}/subscriptions/{{ subscription_id }}/unsubscribe" style="color: #ef4444;">取消此关键词订阅</a></p>
            <p style="margin-top: 15px;">© 2025 CMS-WHUT | 武汉理工大学新闻管理系统</p>
        </div>
    </div>
</body>
</html>
"""


# Create global email service instance
email_service = EmailService()
