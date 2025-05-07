import pytest
from pydantic import ValidationError

from app.models.schemas import UserBase, UserCreate, UserResponse, UserUpdate


def test_valid_telegram_handle():
    """Test that valid Telegram handles are accepted."""
    user = UserBase(telegram_handle="@validuser")
    assert user.telegram_handle == "@validuser"


def test_invalid_telegram_handle():
    """Test that invalid Telegram handles are rejected."""
    with pytest.raises(ValidationError):
        UserBase(telegram_handle="invalid_no_at")

    with pytest.raises(ValidationError):
        UserBase(telegram_handle="@ab")  # Too short

    with pytest.raises(ValidationError):
        # Telegram handles are max 32 characters
        UserBase(telegram_handle="@" + "a" * 33)


def test_reminder_days_validation():
    """Test that reminder_days is validated correctly."""
    # Valid values
    user1 = UserBase(reminder_days=0)
    assert user1.reminder_days == 0

    user2 = UserBase(reminder_days=30)
    assert user2.reminder_days == 30

    # Invalid values
    with pytest.raises(ValidationError):
        UserBase(reminder_days=-1)

    with pytest.raises(ValidationError):
        UserBase(reminder_days=31)


def test_user_create_validation():
    """Test that UserCreate validates clerk_id correctly."""
    # Valid clerk_id
    user = UserCreate(clerk_id="valid_clerk_id")
    assert user.clerk_id == "valid_clerk_id"

    # clerk_id is required
    with pytest.raises(ValidationError):
        UserCreate()

    # Empty clerk_id is invalid
    with pytest.raises(ValidationError):
        UserCreate(clerk_id="")


def test_user_update_optional_fields():
    """Test that UserUpdate fields are all optional."""
    # All fields can be omitted
    user = UserUpdate()
    assert user.telegram_handle is None
    assert user.reminder_days == 0

    # Can update just one field
    user_tg = UserUpdate(telegram_handle="@testuser")
    assert user_tg.telegram_handle == "@testuser"
    assert user_tg.reminder_days == 0

    user_days = UserUpdate(reminder_days=7)
    assert user_days.telegram_handle is None
    assert user_days.reminder_days == 7
