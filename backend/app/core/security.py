from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.user import User
from app.database.connection import get_db
from datetime import datetime, timedelta, timezone

import uuid
from pwdlib import PasswordHash
import jwt
import os
from dotenv import load_dotenv
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from app.core.config import settings

load_dotenv()

password_hash = PasswordHash.recommended()


def hash_pass(password: str) -> str:
    return password_hash.hash(password)


def verify_pass(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {"sub": user_id, "exp": expires_at, "type": "access"}

    return jwt.encode(
        payload,
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM"),
    )


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[settings.JWT_ALGORITHM],
        )

        if payload.get("type") != "access":
            return

        user_id = payload.get("sub")
        if not user_id:
            return None

        return payload
    except jwt.InvalidTokenError:
        return None


def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def gen_random_device_id():
    device_id = str(uuid.uuid4())
    return device_id

def gen_random_credential():
    credentials = secrets.token_urlsafe(32)
    return credentials

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW_Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW_Authenticate": "Bearer"},
        )

    user = db.query(User).where(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW_Authenticate": "Bearer"},
        )

    return user


def get_current_admin(current_user=Depends(get_current_user)):
    if current_user.username != "zico":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin acces required"
        )
    return current_user
