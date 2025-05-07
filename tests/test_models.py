import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.models.models import User

# Create a test database in memory
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    # Create the tables
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
    """Test creating a user in the database."""
    # Create a user
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)

    # Add to the session and commit
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Check the user was created correctly
    assert user.id is not None
    assert user.clerk_id == "test_clerk_id"
    assert user.telegram_handle == "@testuser"
    assert user.reminder_days == 1
    assert user.created_at is not None
    assert user.updated_at is not None


def test_get_user_by_clerk_id(db_session):
    """Test retrieving a user by clerk_id."""
    # Create a user
    user = User(
        clerk_id="test_clerk_id_2", telegram_handle="@testuser2", reminder_days=2
    )

    # Add to the session and commit
    db_session.add(user)
    db_session.commit()

    # Retrieve the user by clerk_id
    retrieved_user = (
        db_session.query(User).filter(User.clerk_id == "test_clerk_id_2").first()
    )

    # Check the user was retrieved correctly
    assert retrieved_user is not None
    assert retrieved_user.clerk_id == "test_clerk_id_2"
    assert retrieved_user.telegram_handle == "@testuser2"
    assert retrieved_user.reminder_days == 2
