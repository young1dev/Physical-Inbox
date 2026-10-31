from fastapi import status, HTTPException, APIRouter, Depends
from app.schemas.auth import AddDevice
from app.models.configdevice import ConfiguredDevice
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import get_current_admin
from app.core.security import (
    hash_pass,
    verify_pass,
)

router=APIRouter(prefix="/device/config", tags=["Device Configuratiom"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def adddevice(payload: AddDevice, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    device_id = payload.device_id
    credentials_hash=hash_pass(payload.credentials)
    
    device = ConfiguredDevice(
        device_id=device_id,
        credentials_hash=credentials_hash
    )
    