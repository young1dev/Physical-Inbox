from fastapi import FastAPI
from app.routers.health import router as health_router 
from app.routers.auth import router as auth_router
from app.routers.pair import router as pair_router
from app.routers.configdevice import router as adddevice_router
from app.routers.google_oauth import router as google_oauth_router

from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=str(os.getenv("SESSION_SECRET_KEY")),
    same_site="lax",
    https_only=False, # Change to True in production
)

app.include_router(auth_router)
app.include_router(pair_router)
app.include_router(adddevice_router)
app.include_router(google_oauth_router)
app.include_router(health_router)
