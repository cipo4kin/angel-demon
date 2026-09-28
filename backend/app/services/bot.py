import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from app.config import settings

bot_router = Router()
bot = Bot(token=settings.BOT_TOKEN) if settings.BOT_TOKEN else None
dp = Dispatcher()


@bot_router.message(CommandStart())
async def cmd_start(message: Message):
    webapp_url = settings.WEBAPP_URL or "https://angel-demon.duckdns.org"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡️ Рассудить дилемму",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        ]
    )
    welcome_text = (
        "👋 **Добро пожаловать в «Ангел и Демон»!**\n\n"
        "Стоишь перед сложным выбором и сомневаешься?\n\n"
        "Твою ситуацию разберут две противоположные стороны:\n"
        "🕊 **Ангел** - совесть, разум и спокойствие\n"
        "🔥 **Демон** - циничный эгоизм и горькая правда\n"
        "🔮 **Судья** - беспристрастный психологический вердикт\n\n"
        "Жми кнопку ниже, чтобы открыть приложение:"
    )
    await message.answer(welcome_text, reply_markup=keyboard, parse_mode="Markdown")


dp.include_router(bot_router)