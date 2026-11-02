from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.auth import PairDevice
from app.models.device import Device
from app.models.configdevice import ConfiguredDevice
from app.core.security import get_current_user
from app.core.security import (
    hash_pass,
    verify_pass,
)

from sqlalchemy.orm import Session
from app.database.connection import get_db

router = APIRouter(prefix="/auth/pair", tags=["Device Authentication"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def pair(payload: PairDevice, db: Session = Depends(get_db), current_user= Depends(get_current_user)):
    device_id = payload.device_id
    user_id = current_user.id
    credentials = payload.credentials
    credentials_hash = hash_pass(payload.credentials)
    name = "Device 1"

    configdevice = (
        db.query(ConfiguredDevice).filter((ConfiguredDevice.device_id == device_id))
    ).first()

    if not configdevice:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid ID/credentials or password,",
        )
    if configdevice.status:
        raise HTTPException(
            status_code=status.HTTP_226_IM_USED, detail="Device is already paired"
        )

    if not verify_pass(credentials, configdevice.credential_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid ID/credentials or password",
        )

    device = Device(user_id=user_id, credential_hash=credentials_hash, name=name)

    db.add(device)
    configdevice.status = True
    db.commit()
