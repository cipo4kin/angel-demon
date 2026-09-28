import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.api.security import get_current_user_id
from app.database.db import get_db
from app.database.queries import choose_side, get_or_create_user, get_user_history, save_dilemma, spend_judge_sphere
from app.services.llm import generate_duality, generate_response
from app.services.prompts import JUDGE_SYSTEM, format_judge_input, get_skin_prompts
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
    judge_answer = None
    if req.use_judge:
        has_sphere = await spend_judge_sphere(db, user_id)
        if not has_sphere:
            raise HTTPException(status_code=400, detail="Недостаточно сфер судьи! Пополните баланс в магазине.")
    angel_prompt, demon_prompt = get_skin_prompts(req.skin)
    angel_answer, demon_answer, elapsed = await generate_duality(
        angel_prompt, demon_prompt, req.text
    )
    if req.use_judge:
        judge_input = format_judge_input(req.text, angel_answer, demon_answer)
        judge_answer, _ = await generate_response(JUDGE_SYSTEM, judge_input)
    dilemma_id = await save_dilemma(
        db, user_id, req.text, req.skin, angel_answer, demon_answer
    )
    user = await get_or_create_user(db, user_id)

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


   