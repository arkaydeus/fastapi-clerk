from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class UserBase(BaseModel):
    """Base model for user data."""

    telegram_handle: Optional[str] = Field(
        None,
        description="User's Telegram handle, e.g. @username",
        pattern=r"^@[\w\d_]{5,32}$",
        examples=["@johndoe", "@telegramuser"],
    )
    reminder_days: Optional[int] = Field(
        0,
        description="Days before event to send reminder. 0 means on the day.",
        ge=0,
        le=30,
        examples=[0, 1, 7],
    )


class UserCreate(UserBase):
    """Model for creating a new user."""

    clerk_id: str = Field(
        ...,  # ... means required
        description="Unique identifier from Clerk authentication",
        min_length=1,
        examples=["user_2vVhPFej8Kl2dBHl5Zxc8LvuKb1"],
    )


class UserUpdate(UserBase):
    """Model for updating user data."""

    pass


class UserResponse(UserBase):
    """Model for user response data."""

    id: int = Field(..., description="Unique database identifier")
    clerk_id: str = Field(
        ..., description="Unique identifier from Clerk authentication"
    )
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: datetime = Field(
        ..., description="Timestamp when the user was last updated"
    )

    class Config:
        from_attributes = True  # Replaces orm_mode in Pydantic V2
