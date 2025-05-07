from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/db-test", tags=["db-test"])


@router.get("/ping")
async def ping_database(db: Session = Depends(get_db)):
    """
    Test database connectivity by executing a simple query.

    Args:
        db: Database session

    Returns:
        dict: Connection status
    """
    try:
        # Execute a simple query to check connection
        result = db.execute(text("SELECT 1")).scalar()
        return {"status": "connected", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}",
        )
