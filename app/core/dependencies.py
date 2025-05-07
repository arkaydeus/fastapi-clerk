from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.core.auth import get_current_clerk_id


async def get_clerk_id(request: Request) -> str:
    """
    Get the Clerk ID from the request state.

    Args:
        request: The FastAPI request

    Returns:
        str: The Clerk user ID

    Raises:
        HTTPException: If the user is not authenticated
    """
    clerk_id = request.state.clerk_id
    if clerk_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return clerk_id


async def get_optional_clerk_id(request: Request) -> Optional[str]:
    """
    Get the Clerk ID from the request state, if available.

    Args:
        request: The FastAPI request

    Returns:
        str: The Clerk user ID if available, None otherwise
    """
    return getattr(request.state, "clerk_id", None)


# For backward compatibility with existing code
# This allows both dependency approaches to work
get_current_user_id = get_clerk_id
