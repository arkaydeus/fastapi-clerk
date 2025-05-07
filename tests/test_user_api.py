from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.dependencies import get_clerk_id
from app.db.database import Base, get_db
from app.main import app
from app.models.models import User

# Create a test database in memory
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db dependency for testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override auth dependency for testing
async def override_get_clerk_id(request):
    return "test_clerk_id"


# Apply the overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_clerk_id] = override_get_clerk_id

# Create a test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    # Create the tables
    Base.metadata.create_all(bind=engine)

    # Create a test user
    db = TestingSessionLocal()
    user = User(clerk_id="test_clerk_id", telegram_handle="@testuser", reminder_days=1)
    db.add(user)
    db.commit()
    db.close()

    yield

    # Drop the tables
    Base.metadata.drop_all(bind=engine)


def test_get_current_user_exists(setup_database):
    """Test GET /users/me when user exists."""
    response = client.get("/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["clerk_id"] == "test_clerk_id"
    assert data["telegram_handle"] == "@testuser"
    assert data["reminder_days"] == 1


def test_get_current_user_new():
    """Test GET /users/me when user doesn't exist (creates new user)."""
    # Drop and recreate the tables to ensure no user exists
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    response = client.get("/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["clerk_id"] == "test_clerk_id"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_update_user_preferences(setup_database):
    """Test PATCH /users/me to update user preferences."""
    response = client.patch(
        "/users/me", json={"telegram_handle": "@updated", "reminder_days": 3}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_handle"] == "@updated"
    assert data["reminder_days"] == 3


def test_update_user_partial(setup_database):
    """Test PATCH /users/me with partial update."""
    # Only update the telegram handle
    response = client.patch("/users/me", json={"telegram_handle": "@partial"})

    assert response.status_code == 200
    data = response.json()
    assert data["telegram_handle"] == "@partial"
    assert data["reminder_days"] == 1  # Should be unchanged


def test_delete_user(setup_database):
    """Test DELETE /users/me."""
    response = client.delete("/users/me")

    assert response.status_code == 204

    # Verify user is deleted
    db = TestingSessionLocal()
    user = db.query(User).filter(User.clerk_id == "test_clerk_id").first()
    db.close()
    assert user is None
