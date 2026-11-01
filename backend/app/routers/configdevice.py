from fastapi import status, HTTPException, APIRouter, Depends
from app.models.configdevice import ConfiguredDevice
from sqlalchemy.orm import Session

from app.core.security import gen_random_device_id, gen_random_credential
from app.database.connection import get_db
from app.core.security import get_current_admin
from app.core.security import (
    hash_pass,)

router=APIRouter(prefix="/device/config", tags=["Device Configuratiom"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def adddevice(db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    device_id = gen_random_device_id()
    credentials = gen_random_credential()
    
    credentials_hash=hash_pass(credentials)
    
    device = ConfiguredDevice(
        device_id=device_id,
        credential_hash=credentials_hash,
    )
    
    try:
        db.add(device)
        db.commit()
        db.refresh(device)
        
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create a device"
        )
    
    return {
        "device_id": device.device_id,
        "credentials": credentials,
    }