from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_clerk_id
from app.core.logging import logger
from app.db.database import get_db
from app.models.schemas import UserResponse, UserUpdate
from app.services.user_service import (
    delete_user,
    get_or_create_user,
    get_user_by_clerk_id,
    get_user_by_id,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get the current authenticated user or create a new one if not found.",
)
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Get the current authenticated user or create them if they don't exist.

    This endpoint:
    1. Gets the user's Clerk ID from the authentication token
    2. Checks if a user with that Clerk ID exists in the database
    3. Creates a new user if one doesn't exist
    4. Returns the user data

    Args:
        request: The FastAPI request containing authentication info
        db: Database session dependency

    Returns:
        UserResponse: The user data object

    Raises:
        HTTPException: If authentication fails
    """
    logger.info("Get current user endpoint accessed")

    try:
        clerk_id = await get_clerk_id(request)
        logger.info(
            "Authenticated user accessing their profile", extra={"clerk_id": clerk_id}
        )

        user = get_or_create_user(db, clerk_id)

        logger.info(
            "User retrieved successfully",
            extra={
                "user_id": user.id,
                "clerk_id": user.clerk_id,
                "has_telegram": user.telegram_handle is not None,
            },
        )

        return user
    except Exception as e:
        logger.error("Error in get current user endpoint", exc_info=e)
        raise


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update User Preferences",
    description="Update the current user's preferences like telegram handle and reminder days.",
)
async def update_current_user(
    preferences: UserUpdate, request: Request, db: Session = Depends(get_db)
):
    """
    Update the current user's preferences.

    This endpoint allows updating:
    - Telegram handle
    - Reminder days setting

    Args:
        preferences: User preferences data to update
        request: The FastAPI request containing authentication info
        db: Database session dependency

    Returns:
        UserResponse: The updated user data

    Raises:
        HTTPException: If user not found or update fails
    """
    logger.info("Update user preferences endpoint accessed")

    try:
        clerk_id = await get_clerk_id(request)
        logger.info(
            "User attempting to update preferences",
            extra={
                "clerk_id": clerk_id,
                "update_fields": {
                    "telegram_handle": preferences.telegram_handle is not None,
                    "reminder_days": preferences.reminder_days is not None,
                },
            },
        )

        user = get_user_by_clerk_id(db, clerk_id)

        if not user:
            logger.warning(
                "User not found during update attempt", extra={"clerk_id": clerk_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        updated_user = update_user(db, user, preferences)

        logger.info(
            "User preferences updated successfully",
            extra={"user_id": updated_user.id, "clerk_id": updated_user.clerk_id},
        )

        return updated_user
    except HTTPException:
        # Re-raise HTTP exceptions without logging as they're already logged
        raise
    except Exception as e:
        logger.error("Unexpected error in update user preferences", exc_info=e)
        raise


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Current User",
    description="Delete the current user's account completely.",
)
async def delete_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Delete the current user.

    This endpoint completely removes the user account from the database.
    Note: This does not delete the user from Clerk, only from our database.

    Args:
        request: The FastAPI request containing authentication info
        db: Database session dependency

    Returns:
        None: No content response on success

    Raises:
        HTTPException: If user not found or deletion fails
    """
    logger.info("Delete user endpoint accessed")

    try:
        clerk_id = await get_clerk_id(request)
        logger.info(
            "User attempting to delete their account", extra={"clerk_id": clerk_id}
        )

        user = get_user_by_clerk_id(db, clerk_id)

        if not user:
            logger.warning(
                "User not found during deletion attempt", extra={"clerk_id": clerk_id}
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        delete_user(db, user)

        logger.info("User deleted successfully", extra={"clerk_id": clerk_id})

        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        # Re-raise HTTP exceptions without logging as they're already logged
        raise
    except Exception as e:
        logger.error("Unexpected error in delete user endpoint", exc_info=e)
        raise
