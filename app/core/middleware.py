from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.auth import optional_clerk_auth
from app.core.logging import logger


class ClerkAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling Clerk authentication.
    Adds the clerk_id to the request state if available.
    """

    def __init__(self, app: ASGIApp, public_paths: list[str] = None):
        """
        Initialize the middleware.

        Args:
            app: The ASGI app
            public_paths: List of paths that don't require authentication
        """
        super().__init__(app)
        self.public_paths = public_paths or [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        # Log the public paths during initialization
        logger.debug(
            f"ClerkAuthMiddleware initialized with public_paths: {self.public_paths}"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request, adding the clerk_id to the request state if available.

        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain

        Returns:
            Response: The response from the next middleware/handler
        """
        path = request.url.path
        logger.debug(f"Processing request for path: {path}")

        # Check if the path is public
        is_public = False

        # First check for exact matches
        if path in self.public_paths:
            logger.debug(f"Path '{path}' is an exact match to public path")
            is_public = True
        else:
            # Then check for prefix matches (for routes like /docs/*)
            for public_path in self.public_paths:
                # Exact api endpoints should not match by prefix
                if path.startswith("/api/") and not public_path.startswith("/api/"):
                    continue

                # Special case: Don't treat /users/me as public even if / is public
                if path == "/users/me" and public_path == "/":
                    continue

                # Normal prefix matching
                if path.startswith(public_path):
                    logger.debug(
                        f"Path '{path}' matched public path prefix '{public_path}'"
                    )
                    is_public = True
                    break

        # No auth check needed for public paths
        if is_public:
            logger.debug(f"Skipping auth for public path: {path}")
            return await call_next(request)

        # Try to get the clerk_id without raising an exception
        logger.debug(f"Authenticating request for path: {path}")
        clerk_id = await optional_clerk_auth(request)

        # Add to request state if available
        request.state.clerk_id = clerk_id
        logger.debug(f"Set clerk_id in request state: {clerk_id}")

        # Continue processing the request
        return await call_next(request)


def add_clerk_middleware(app: FastAPI, public_paths: list[str] = None) -> None:
    """
    Add the Clerk authentication middleware to the FastAPI app.

    Args:
        app: The FastAPI app
        public_paths: List of paths that don't require authentication
    """
    app.add_middleware(
        ClerkAuthMiddleware,
        public_paths=public_paths,
    )
