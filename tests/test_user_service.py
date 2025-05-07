import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.models import User
from app.models.schemas import UserCreate, UserUpdate
from app.services.user_service import (
    create_user,
    delete_user,
    get_or_create_user,
    get_user_by_clerk_id,
    get_user_by_id,
    get_user_by_telegram_handle,
    update_user,
)

# Create a test database in memory
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    # Create the tables using models that inherit from Base
    Base.metadata.create_all(bind=engine)

    # Create a session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()

    # Drop the tables
    Base.metadata.drop_all(bind=engine)


def test_create_user(db_session):
    """Test creating a user."""
    user_data = UserCreate(
        clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1
    )

    user = create_user(db_session, user_data)

    assert user.id is not None
    assert user.clerk_id == "test_clerk_id"
    assert user.telegram_handle == "@testuser"
    assert user.reminder_days == 1
    assert user.created_at is not None
    assert user.updated_at is not None


def test_get_user_by_clerk_id(db_session):
    """Test getting a user by clerk_id."""
    # Create a user first
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db_session.add(user)
    db_session.commit()

    # Retrieve the user
    retrieved_user = get_user_by_clerk_id(db_session, "test_clerk_id")

    assert retrieved_user is not None
    assert retrieved_user.clerk_id == "test_clerk_id"

    # Test non-existent user
    nonexistent_user = get_user_by_clerk_id(db_session, "nonexistent_id")
    assert nonexistent_user is None


def test_get_user_by_id(db_session):
    """Test getting a user by database ID."""
    # Create a user first
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db_session.add(user)
    db_session.commit()

    # Retrieve the user
    retrieved_user = get_user_by_id(db_session, user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == user.id

    # Test non-existent user
    nonexistent_user = get_user_by_id(db_session, 9999)
    assert nonexistent_user is None


def test_get_user_by_telegram_handle(db_session):
    """Test getting a user by telegram handle."""
    # Create a user first
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db_session.add(user)
    db_session.commit()

    # Retrieve the user
    retrieved_user = get_user_by_telegram_handle(db_session, "@testuser")

    assert retrieved_user is not None
    assert retrieved_user.telegram_handle == "@testuser"

    # Test non-existent user
    nonexistent_user = get_user_by_telegram_handle(db_session, "@nonexistent")
    assert nonexistent_user is None


def test_update_user(db_session):
    """Test updating a user."""
    # Create a user first
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db_session.add(user)
    db_session.commit()

    # Update the user
    update_data = UserUpdate(telegram_handle="@newhandle", reminder_days=2)

    updated_user = update_user(db_session, user, update_data)

    assert updated_user.telegram_handle == "@newhandle"
    assert updated_user.reminder_days == 2


def test_delete_user(db_session):
    """Test deleting a user."""
    # Create a user first
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db_session.add(user)
    db_session.commit()

    # Delete the user
    result = delete_user(db_session, user)

    assert result is True

    # Verify the user is deleted
    deleted_user = get_user_by_clerk_id(db_session, "test_clerk_id")
    assert deleted_user is None


def test_get_or_create_user_existing(db_session):
    """Test get_or_create_user with an existing user."""
    # Create a user first
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db_session.add(user)
    db_session.commit()

    # Get the existing user
    result = get_or_create_user(db_session, "test_clerk_id")

    assert result is not None
    assert result.clerk_id == "test_clerk_id"
    assert result.telegram_handle == "@testuser"
    assert result.reminder_days == 1


def test_get_or_create_user_new(db_session):
    """Test get_or_create_user creating a new user."""
    # Get or create a new user
    result = get_or_create_user(
        db_session, "new_clerk_id", telegram_handle="@newuser", reminder_days=3
    )

    assert result is not None
    assert result.clerk_id == "new_clerk_id"
    assert result.telegram_handle == "@newuser"
    assert result.reminder_days == 3

    # Verify the user was created in the database
    created_user = get_user_by_clerk_id(db_session, "new_clerk_id")
    assert created_user is not None
