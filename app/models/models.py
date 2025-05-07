from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base


class User(Base):
    """
    User model for storing user information from Clerk authentication.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clerk_id = Column(String(255), unique=True, index=True, nullable=False)
    telegram_handle = Column(String(255), nullable=True)
    reminder_days = Column(Integer, default=0)  # 0 = on the day, 1 = 1 day before, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
