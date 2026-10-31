from fastapi import APIRouter, Depends

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.connection import get_db

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("/db")
def health_check(db: Session = Depends(get_db)):
    verify_db_connection = db.execute(text("SELECT version()")).scalar()
    return {"status": "healthy", "db_version": verify_db_connection}

