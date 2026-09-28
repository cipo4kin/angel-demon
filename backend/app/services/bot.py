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

from aiogram import F
from aiogram.types import PreCheckoutQuery
import aiosqlite
from app.database.queries import add_judge_spheres, unlock_skin

@bot_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@bot_router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    parts = payload.split(":")
    if len(parts) == 2:
        item, user_id_str = parts
        user_id = int(user_id_str)
        async with aiosqlite.connect(settings.DB_PATH) as db:
            if item == "pack_spheres":
                await add_judge_spheres(db, user_id, 3)
            elif item in ("skin_gopnik", "skin_office"):
                skin_name = item.replace("skin_", "")
                await unlock_skin(db, user_id, skin_name)

    await message.answer("🎉 Оплата через Telegram Stars прошла успешно! Товары добавлены в твой профиль.")


dp.include_router(bot_router)