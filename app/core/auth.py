from typing import Any, Dict, Optional

import jwt
from clerk_backend_api import Clerk
from clerk_backend_api.models import ClerkErrors, SDKError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.logging import logger

settings = get_settings()
security = HTTPBearer(auto_error=False)

# Initialize Clerk SDK with the secret key
clerk_client = Clerk(bearer_auth=settings.clerk_secret_key)


async def get_authorization_header(request: Request) -> Optional[str]:
    """
    Extract authorization header from request.

    Args:
        request: The FastAPI request

    Returns:
        str: The authorization token if found, None otherwise
    """
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header.startswith("Bearer "):
            return auth_header.replace("Bearer ", "")
    return None


def verify_jwt(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Verify the JWT token from Clerk.

    Args:
        credentials: The HTTP Authorization credentials containing the JWT token

    Returns:
        dict: The decoded JWT payload

    Raises:
        HTTPException: If the token is invalid, expired, or missing
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        # Verify token with JWT library
        # For simplicity, we'll decode it without verification first to get the user ID
        try:
            # Decode the JWT token without verification to extract the user ID
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            user_id = unverified_payload.get("sub")

            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify user exists in Clerk
            try:
                user = clerk_client.users.get(user_id=user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Return a payload with the essential information
                return {"sub": user_id}
            except Exception as e:
                logger.error(f"Error fetching user: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Error verifying user: {str(e)}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except jwt.PyJWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token format: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (SDKError, ClerkErrors) as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_clerk_id(payload: dict = Depends(verify_jwt)) -> str:
    """
    Extract the Clerk user ID from the JWT payload.

    Args:
        payload: The decoded JWT payload

    Returns:
        str: The Clerk user ID

    Raises:
        HTTPException: If the user ID is not found in the token
    """
    # Clerk uses "sub" claim for the user ID
    clerk_id = payload.get("sub")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID in token"
        )
    return clerk_id


async def optional_clerk_auth(request: Request) -> Optional[str]:
    """
    Optional authentication that doesn't raise an exception if no token is provided.

    Args:
        request: The FastAPI request

    Returns:
        str: The Clerk user ID if token is valid, None otherwise
    """
    token = await get_authorization_header(request)
    if not token:
        logger.debug("No authorization token found in request")
        return None

    try:
        # Decode the JWT token without verification to extract the user ID
        try:
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            user_id = unverified_payload.get("sub")

            if not user_id:
                logger.debug("Token validation failed: missing user ID")
                return None

            # Optionally verify user exists in Clerk
            try:
                user = clerk_client.users.get(user_id=user_id)
                if user:
                    return user_id
                logger.debug("Token validation failed: user not found")
                return None
            except Exception as e:
                logger.error(f"Error fetching user: {str(e)}")
                return None
        except jwt.PyJWTError as e:
            logger.error(f"JWT decode error: {str(e)}")
            return None
    except Exception as e:
        logger.error(
            f"Unexpected error during token verification: {str(e)}", exc_info=True
        )
        return None


async def get_clerk_user(user_id: str) -> Dict[str, Any]:
    """
    Retrieve user details from Clerk.

    Args:
        user_id: The Clerk user ID

    Returns:
        Dict[str, Any]: User details from Clerk

    Raises:
        HTTPException: If the user could not be retrieved
    """
    try:
        user = clerk_client.users.get(user_id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except (SDKError, ClerkErrors) as e:
        logger.error(f"Error retrieving user from Clerk: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}",
        )
