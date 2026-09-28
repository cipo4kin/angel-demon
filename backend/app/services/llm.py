import asyncio
import time
import groq
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
async def main():
    print(f"Модель: {settings.GROQ_MODEL}")
    print("Рассуждаем дилемму одновременно: Ангел и Демон...\n")

    dilemma = "Стоит ли брать кредит на новый айфон?"

    angel_prompt = (
        "Ты мудрый, добрый ангел-хранитель. Ответь конструктивно, тепло и разумно в 1-2 предложениях на русском."
    )
    demon_prompt = (
        "Ты циничный, язвительный демон-искуситель. Ответь с черным юмором и сарказмом в 1-2 предложениях на русском."
    )

    start_total = time.perf_counter()
    
    (angel_text, _), (demon_text, _) = await asyncio.gather(
        generate_response(angel_prompt, dilemma),
        generate_response(demon_prompt, dilemma),
    )
    total_time = time.perf_counter() - start_total

    print(f"🕊 АНГЕЛ:\n{angel_text}\n")
    print(f"🔥 ДЕМОН:\n{demon_text}\n")
    print(f"Общее время параллельной генерации: {total_time:.2f} сек\n")


asyncio.run(main())
