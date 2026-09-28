from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import router as api_router
from app.config import settings
from app.database.db import init_db

import asyncio
from app.services.bot import bot, dp

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    polling_task = None
    if bot:
        polling_task = asyncio.create_task(dp.start_polling(bot))
        print("Бот и Бэк запущены")
    else:
        print("Бэк запущен (без бота)")
    yield
    if polling_task:
        polling_task.cancel()
    if bot:
        await bot.session.close()
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