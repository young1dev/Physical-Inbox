from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from google_auth_oauthlib.flow import Flow
from uuid import UUID
from app.core.encryption import encrypt_token, decrypt_token
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleRequest
import os
from dotenv import load_dotenv
from app.core.security import get_current_user

from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.google_conn import GoogleConnection

load_dotenv()

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [REDIRECT_URI],
    }
}

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])


@router.get("/connect")
def connect_google(
    request: Request,
    current_user=Depends(get_current_user),
):
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    request.session["google_oauth_state"] = state
    request.session["google_user_id"] = str(current_user.id)

    return {"authorization_url": authorization_url}


@router.get("/callback")
def google_callback(
    request: Request,
    state: str,
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authorization failed",
        )
    stored_state = request.session.pop("google_oauth_state", None)
    user_id = request.session.pop("google_user_id", None)

    if not stored_state or stored_state != state or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Oauth session. Please try again.",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code missing"
        )

    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI,
    )

    flow.fetch_token(code=code)

    credentials = flow.credentials

    identity = id_token.verify_oauth2_token(
        credentials.id_token,
        GoogleRequest(),
        CLIENT_ID,
    )
    granted_scopes = credentials.granted_scopes or credentials.scopes or []

    email_verified = identity["email_verified"]

    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Google email not verified"
        )

    user_uuid = UUID(user_id)


    existing_conn = (
        db.query(GoogleConnection).filter(GoogleConnection.user_id == user_uuid).first()
    )

    # Ensure at least one useful permission was granted
    useful_scopes = {
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/calendar.readonly",
    }

    if not useful_scopes.intersection(granted_scopes):
        raise HTTPException(
            status_code=400, detail="Grant Gmail or Calendar access to continue."
        )

    if existing_conn:
        existing_conn.google_email = identity["email"]
        existing_conn.google_sub = identity["sub"]
        existing_conn.access_token = encrypt_token(credentials.token)
        existing_conn.expires_at = credentials.expiry
        existing_conn.scopes = granted_scopes

        if credentials.refresh_token:
            existing_conn.refresh_token = credentials.refresh_token

    else:
        google_credentials = GoogleConnection(
            user_id=user_uuid,
            google_email=identity["email"],
            google_sub=identity["sub"],
            access_token=encrypt_token(credentials.token),
            refresh_token=encrypt_token(credentials.refresh_token) if credentials.refresh_token else None,
            expires_at=credentials.expiry,
            scopes=granted_scopes,
        )

        db.add(google_credentials)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Failed to save Google credentials. Please try again."
        )

    return {
        "message": "Google account connected successfully",
        "google_email": identity["email"],
        "granted_scopes": granted_scopes,
    }
