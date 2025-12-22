# Database models package
from app.models.news import News
from app.models.user import User, user_bookmarks
from app.models.calendar import Semester, SemesterWeek
from app.models.subscription import KeywordSubscription, NotificationHistory

__all__ = ["News", "User", "user_bookmarks", "Semester", "SemesterWeek", "KeywordSubscription", "NotificationHistory"]
