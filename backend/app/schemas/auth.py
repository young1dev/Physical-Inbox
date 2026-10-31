from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1, max_length=255)


class PairDevice(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=255)
    device_id: str = Field(..., min_length=1, max_length=255)
    credentials: str = Field(..., min_length=1, max_length=255)


class AddDevice(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=255)
    credentials: str = Field(..., min_length=1, max_length=255)