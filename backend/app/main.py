from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import router as api_router
from app.config import settings
from app.database.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Бэк запущен")
    yield
    print("Бэк остановлен")

app = FastAPI(
    title="Ангел и Демон TMA",
    description="Backend API для Telegram Mini App 'Ангел и Демон'",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)

app.include_router(api_router)

if settings.FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=settings.FRONTEND_DIR, html=True),
              name="frontend")