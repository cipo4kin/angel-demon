import logging
import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.api.security import get_current_user_id
from app.database.db import get_db
from app.database.queries import choose_side, get_or_create_user, get_user_history, save_dilemma, spend_judge_sphere
from aiogram.types import LabeledPrice
from app.config import settings
from app.services.bot import bot
from app.services.llm import generate_duality, generate_response
from app.services.prompts import JUDGE_SYSTEM, format_judge_input, get_skin_prompts

logger = logging.getLogger("angel_demon.api")

router = APIRouter(prefix="/api", tags=["API"])

class DilemmaRequest(BaseModel):
    text: str = Field(min_length=3, max_length=500)
    skin: str = Field(default="classic")
    use_judge: bool = Field(default=False)

class ChooseRequest(BaseModel):
    dilemma_id: int = Field(...,)
    side: str = Field(..., pattern="^(angel|demon)$")

@router.get("/me")
async def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    user = await get_or_create_user(db, user_id)
    history = await get_user_history(db, user_id, limit=15)

    return {
        "user": user,
        "history": history
    }
@router.post("/dilemma")
async def create_dilemma(
    req: DilemmaRequest,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    user = await get_or_create_user(db, user_id)
    if req.use_judge and user["judge_spheres"] < 1:
        raise HTTPException(
            status_code=400,
            detail="Недостаточно сфер судьи! Пополните баланс в магазине.",
        )

    skin = req.skin if req.skin in user["unlocked_skins"] else "classic"
    angel_prompt, demon_prompt = get_skin_prompts(skin)

    judge_answer = None
    try:
        angel_answer, demon_answer, elapsed = await generate_duality(
            angel_prompt, demon_prompt, req.text
        )
        if req.use_judge:
            judge_input = format_judge_input(req.text, angel_answer, demon_answer)
            judge_answer, _ = await generate_response(JUDGE_SYSTEM, judge_input)
    except Exception as e:
        logger.exception("Ошибка при генерации ответа сущностей: %s", e)
        raise HTTPException(
            status_code=503,
            detail=str(e) or "Ошибка сервиса нейросети. Попробуйте позже.",
        )

    if req.use_judge:
        await spend_judge_sphere(db, user_id)
        user["judge_spheres"] = max(0, user["judge_spheres"] - 1)

    dilemma_id = await save_dilemma(
        db, user_id, req.text, skin, angel_answer, demon_answer
    )

    return {
        "id": dilemma_id,
        "angel_answer": angel_answer,
        "demon_answer": demon_answer,
        "judge_answer": judge_answer,
        "elapsed": round(elapsed, 2),
        "judge_spheres": user["judge_spheres"],
    }
@router.post("/choose")
async def make_choice(
    req: ChooseRequest,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    karma = await choose_side(db, req.dilemma_id, user_id, req.side)
    return {"karma": karma}


class InvoiceRequest(BaseModel):
    item: str = Field(..., pattern="^(pack_spheres|skin_gopnik|skin_office)$")


@router.post("/create-invoice")
async def create_invoice(
    req: InvoiceRequest,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    if not bot:
        raise HTTPException(
            status_code=500, detail="Telegram бот не настроен"
        )

    if req.item in ("skin_gopnik", "skin_office"):
        skin_name = req.item.replace("skin_", "")
        user = await get_or_create_user(db, user_id)
        if skin_name in user["unlocked_skins"]:
            raise HTTPException(
                status_code=400,
                detail="Этот скин уже разблокирован в вашем профиле!",
            )

    ITEMS_CONFIG = {
        "pack_spheres": {
            "title": "Пак сфер Судьи (3 шт.)",
            "description": "3 сферы для глубокого философского разбора дилемм",
            "amount": settings.PRICE_JUDGE_PACK_3,
        },
        "skin_office": {
            "title": "Скин «Офисный душнила»",
            "description": "Разбор дилемм через KPI, ROI и корпоративные интриги",
            "amount": settings.PRICE_SKIN_OFFICE,
        },
        "skin_gopnik": {
            "title": "Скин «Гопник»",
            "description": "Пояснит на кортах по понятиям и без соплей",
            "amount": settings.PRICE_SKIN_GOPNIK,
        },
    }

    item_info = ITEMS_CONFIG[req.item]
    try:
        invoice_link = await bot.create_invoice_link(
            title=item_info["title"],
            description=item_info["description"],
            payload=f"{req.item}:{user_id}",
            provider_token="",  # Для Telegram Stars provider_token всегда пустой
            currency="XTR",  # Код валюты Telegram Stars
            prices=[
                LabeledPrice(
                    label=item_info["title"], amount=item_info["amount"]
                )
            ],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка генерации счёта: {str(e)}"
        )

    return {"invoice_link": invoice_link}



   