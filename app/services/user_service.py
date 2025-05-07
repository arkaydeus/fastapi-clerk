from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.models import User
from app.models.schemas import UserCreate, UserUpdate


def get_user_by_clerk_id(db: Session, clerk_id: str) -> Optional[User]:
    """
    Get a user by their Clerk ID.

    Args:
        db: Database session
        clerk_id: Clerk user ID

    Returns:
        User: The user if found, None otherwise
    """
    logger.debug(f"Fetching user by clerk_id", extra={"props": {"clerk_id": clerk_id}})
    user = db.query(User).filter(User.clerk_id == clerk_id).first()

    if user:
        logger.debug(
            "User found", extra={"props": {"clerk_id": clerk_id, "user_id": user.id}}
        )
    else:
        logger.debug("User not found", extra={"props": {"clerk_id": clerk_id}})

    return user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by their database ID.

    Args:
        db: Database session
        user_id: Database ID

    Returns:
        User: The user if found, None otherwise
    """
    logger.debug("Fetching user by ID", extra={"props": {"user_id": user_id}})
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        logger.debug(
            "User found",
            extra={"props": {"user_id": user_id, "clerk_id": user.clerk_id}},
        )
    else:
        logger.debug("User not found", extra={"props": {"user_id": user_id}})

    return user


def get_user_by_telegram_handle(db: Session, telegram_handle: str) -> Optional[User]:
    """
    Get a user by their Telegram handle.

    Args:
        db: Database session
        telegram_handle: Telegram handle

    Returns:
        User: The user if found, None otherwise
    """
    logger.debug(
        "Fetching user by telegram handle",
        extra={"props": {"telegram_handle": telegram_handle}},
    )
    user = db.query(User).filter(User.telegram_handle == telegram_handle).first()

    if user:
        logger.debug(
            "User found",
            extra={"props": {"telegram_handle": telegram_handle, "user_id": user.id}},
        )
    else:
        logger.debug(
            "User not found", extra={"props": {"telegram_handle": telegram_handle}}
        )

    return user


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user_data: User data for creation

    Returns:
        User: The created user

    Raises:
        HTTPException: If user creation fails
    """
    logger.info(
        "Creating new user",
        extra={
            "props": {
                "clerk_id": user_data.clerk_id,
                "telegram_handle": user_data.telegram_handle,
            }
        },
    )

    try:
        db_user = User(
            clerk_id=user_data.clerk_id,
            telegram_handle=user_data.telegram_handle,
            reminder_days=user_data.reminder_days,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(
            "User created successfully",
            extra={"props": {"user_id": db_user.id, "clerk_id": db_user.clerk_id}},
        )

        return db_user
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "User creation failed - integrity error",
            extra={
                "props": {
                    "clerk_id": user_data.clerk_id,
                    "telegram_handle": user_data.telegram_handle,
                }
            },
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Clerk ID or Telegram handle already exists",
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "User creation failed - unexpected error",
            extra={"props": {"clerk_id": user_data.clerk_id}},
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


def update_user(db: Session, user: User, user_data: UserUpdate) -> User:
    """
    Update an existing user.

    Args:
        db: Database session
        user: User to update
        user_data: User data for update

    Returns:
        User: The updated user

    Raises:
        HTTPException: If user update fails
    """
    logger.info(
        "Updating user",
        extra={
            "props": {
                "user_id": user.id,
                "clerk_id": user.clerk_id,
                "new_telegram_handle": user_data.telegram_handle,
                "new_reminder_days": user_data.reminder_days,
            }
        },
    )

    try:
        # Update fields if provided
        if user_data.telegram_handle is not None:
            user.telegram_handle = user_data.telegram_handle
        if user_data.reminder_days is not None:
            user.reminder_days = user_data.reminder_days

        db.commit()
        db.refresh(user)

        logger.info(
            "User updated successfully",
            extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
        )

        return user
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "User update failed - integrity error",
            extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this Telegram handle already exists",
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "User update failed - unexpected error",
            extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}",
        )


def delete_user(db: Session, user: User) -> bool:
    """
    Delete a user.

    Args:
        db: Database session
        user: User to delete

    Returns:
        bool: True if successful

    Raises:
        HTTPException: If user deletion fails
    """
    logger.info(
        "Deleting user",
        extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
    )

    try:
        db.delete(user)
        db.commit()

        logger.info(
            "User deleted successfully",
            extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
        )

        return True
    except Exception as e:
        db.rollback()
        logger.error(
            "User deletion failed",
            extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}",
        )


def get_or_create_user(
    db: Session, clerk_id: str, telegram_handle: str = None, reminder_days: int = 0
) -> User:
    """
    Get a user by Clerk ID or create one if not found.

    Args:
        db: Database session
        clerk_id: Clerk user ID
        telegram_handle: Optional telegram handle
        reminder_days: Optional reminder days setting

    Returns:
        User: The existing or newly created user
    """
    logger.info("Getting or creating user", extra={"props": {"clerk_id": clerk_id}})

    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        logger.info(
            "User not found, creating new user", extra={"props": {"clerk_id": clerk_id}}
        )
        user_data = UserCreate(
            clerk_id=clerk_id,
            telegram_handle=telegram_handle,
            reminder_days=reminder_days,
        )
        user = create_user(db, user_data)
    else:
        logger.info(
            "User found, returning existing user",
            extra={"props": {"user_id": user.id, "clerk_id": user.clerk_id}},
        )

    return user
