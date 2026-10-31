from fastapi import FastAPI, status, HTTPException, APIRouter, Depends
from app.schemas.auth import AddDevice
from app.models.configdevice import ConfiguredDevice
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import (
    hash_pass,
    verify_pass,
)

router=APIRouter(prefix="/deviceconfig", tags=["Device Configuratiom"])

@router.post("/device/config", status_code=status.HTTP_201_CREATED)
def adddevice(payload: AddDevice, db: Session = Depends(get_db),):
    device_id = payload.device_id
    credentials_hash=hash_pass(payload.credentials)
    
    