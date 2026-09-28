import asyncio
import time
from groq import AsyncGroq
from app.config import settings

def get_groq_client() -> AsyncGroq:
    return AsyncGroq(api_key=settings.GROQ_API_KEY)

async def generate_response(
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
) -> tuple[str, float]:
    client = get_groq_client()
    chosen_model = model or settings.GROQ_MODEL
    start_time = time.perf_counter()
    response = await client.chat.completions.create(
        model=chosen_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=300
    )
    elapsed = time.perf_counter() - start_time
    content = response.choices[0].message.content or ""
    return content.strip(), elapsed
async def generate_duality(
        angel_system_prompt: str,
        demon_system_prompt: str,
        dilemma_text: str,
) -> tuple[str, str, float]:
    start_time = time.perf_counter()
    (angel_text, _), (demon_text, _) = await asyncio.gather(
        generate_response(angel_system_prompt, dilemma_text),
        generate_response(demon_system_prompt, dilemma_text)
    )
    total_elapsed = time.perf_counter() - start_time
    return angel_text, demon_text, total_elapsed