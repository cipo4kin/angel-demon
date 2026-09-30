import asyncio
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import router as api_router
from app.config import settings
from app.database.db import init_db
from app.services.bot import bot, dp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("angel_demon")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    polling_task = None
    if bot:
        polling_task = asyncio.create_task(dp.start_polling(bot))
        logger.info("Бот и Бэк успешно запущены")
    else:
        logger.info("Бэк запущен (без бота)")
    yield
    if polling_task:
        polling_task.cancel()
    if bot:
        await bot.session.close()
    logger.info("Бэк остановлен")

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