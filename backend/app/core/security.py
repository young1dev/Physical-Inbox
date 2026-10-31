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
    expires_at = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    payload = {
        "sub": user_id,
        "exp": expires_at,
        "type": "access"
    }
    
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
            algorithms=[str(os.getenv("JWT_SECRET_KEY"))],
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

def get_current_admin()