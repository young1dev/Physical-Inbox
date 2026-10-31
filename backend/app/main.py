from fastapi import FastAPI
from app.routers.health import router as health_router 
from app.routers.auth import router as auth_router
from app.routers.pair import router as pair_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(pair_router)
app.include_router(health_router)