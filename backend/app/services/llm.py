import asyncio
import itertools
import logging
import time
from groq import AsyncGroq, APIConnectionError, APIStatusError, RateLimitError
from app.config import settings

logger = logging.getLogger("angel_demon.llm")

_clients: list[AsyncGroq] = []
_client_cycle: itertools.cycle | None = None


def get_clients_pool() -> list[AsyncGroq]:
    global _clients, _client_cycle
    if not _clients:
        keys = settings.groq_keys
        if not keys and settings.GROQ_API_KEY:
            keys = [settings.GROQ_API_KEY]
        if not keys:
            logger.warning("GROQ_API_KEYS не настроены в .env")
            keys = [""]
        _clients = [AsyncGroq(api_key=k) for k in keys]
        _client_cycle = itertools.cycle(_clients)
        logger.info("Инициализирован пул Groq клиентов: %d шт.", len(_clients))
    return _clients


def get_next_client() -> AsyncGroq:
    get_clients_pool()
    return next(_client_cycle)


async def generate_response(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
) -> tuple[str, float]:
    pool = get_clients_pool()
    chosen_model = model or settings.GROQ_MODEL
    max_attempts = max(len(pool), 1)
    last_error: Exception | None = None

    start_time = time.perf_counter()

    for attempt in range(max_attempts):
        client = get_next_client()
        try:
            response = await client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            elapsed = time.perf_counter() - start_time
            content = response.choices[0].message.content or ""
            return content.strip(), elapsed

        except RateLimitError as e:
            logger.warning(
                "Groq 429 RateLimit (попытка %d/%d). Переключаем ключ...",
                attempt + 1,
                max_attempts,
            )
            last_error = e
            continue
        except (APIConnectionError, APIStatusError) as e:
            logger.warning(
                "Groq API error (%s, попытка %d/%d): %s",
                type(e).__name__,
                attempt + 1,
                max_attempts,
                e,
            )
            last_error = e
            continue
        except Exception as e:
            logger.exception("Непредвиденная ошибка Groq: %s", e)
            last_error = e
            break

    logger.error("Все ключи Groq исчерпаны или недоступны. Ошибка: %s", last_error)
    raise RuntimeError("Все доступные ключи нейросети временно перегружены. Попробуй через минуту.") from last_error


async def generate_duality(
    angel_system_prompt: str,
    demon_system_prompt: str,
    dilemma_text: str,
) -> tuple[str, str, float]:
    start_time = time.perf_counter()
    (angel_text, _), (demon_text, _) = await asyncio.gather(
        generate_response(angel_system_prompt, dilemma_text),
        generate_response(demon_system_prompt, dilemma_text),
    )
    total_elapsed = time.perf_counter() - start_time
    return angel_text, demon_text, total_elapsed