from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
from app.schemas.auth import UserCreate, LoginRequest, RefreshTokenRequest
from app.database.connection import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import (
    hash_pass,
    verify_pass,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    username = str(payload.username).strip().lower()

    existing_user = db.query(User).filter((User.email == email)).first()

    existing_username = db.query(User).filter((User.username == username)).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this username already exists",
        )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    user = User(
        email=email,
        username=username,
        password_hash=hash_pass(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
    }


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    identifier = str(payload.identifier).strip().lower()
    password = str(payload.password)

    user = (
        db.query(User)
        .filter((User.email == identifier) | (User.username == identifier))
        .first()
    )

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password",
        )

    if not verify_pass(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password",
        )
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()

    refresh_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    refresh_expires_at = datetime.now(timezone.utc) + timedelta(days=refresh_days)

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=refresh_expires_at,
    )
    db.add(refresh_token_record)
    db.commit()

    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/refresh")
def refresh_access_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    token_hash = hash_refresh_token(payload.refresh_token)

    refresh_tokens = (
        db.query(RefreshToken).where(RefreshToken.token_hash == token_hash).first()
    )

    if not refresh_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_tokens.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if refresh_tokens.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    user = db.query(User).where(User.id == refresh_tokens.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    refresh_tokens.revoked_at = datetime.now(timezone.utc)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token()

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    
    db.add(refresh_token_record)
    db.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
