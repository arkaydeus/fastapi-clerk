from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.db_test_router import router as db_test_router
from app.api.user_router import router as user_router
from app.core.logging import logger
from app.core.middleware import add_clerk_middleware

app = FastAPI(
    title="FastAPI-Clerk Authentication Service",
    description="A service to check and create users based on Clerk authentication",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Clerk authentication middleware
add_clerk_middleware(
    app,
    public_paths=[
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/db-test",  # Allow database test without authentication
        "/debug-jwt-key",  # Allow JWT key debugging
        "/debug-jwt-auth",  # Allow JWT auth debugging
        "/debug-jwt-key-detail",  # Allow detailed JWT key debugging
    ],
)

# Include routers
app.include_router(user_router)
app.include_router(db_test_router)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to FastAPI-Clerk Authentication Service"}


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed")
    return {"status": "healthy"}


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors from pydantic.
    """
    error_details = []
    for error in exc.errors():
        error_details.append(
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        "Validation error", extra={"path": request.url.path, "errors": error_details}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": error_details},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors.
    """
    logger.error("Database error", extra={"path": request.url.path}, exc_info=exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An error occurred with the database operation"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle any unhandled exceptions.
    """
    error_message = str(exc)
    logger.error(
        "Unhandled exception",
        extra={"path": request.url.path, "error": error_message},
        exc_info=exc,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )
