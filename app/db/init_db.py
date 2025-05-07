from sqlalchemy_utils import create_database, database_exists

from app.db.database import Base, engine
from app.models.models import (
    User,  # Import all models here to ensure they're registered with Base
)


def init_db():
    """
    Initialize the database, creating it if it doesn't exist
    and creating all tables defined in the models.
    """
    try:
        # Create database if it doesn't exist
        if not database_exists(engine.url):
            create_database(engine.url)
            print(f"Created database at {engine.url}")

        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
