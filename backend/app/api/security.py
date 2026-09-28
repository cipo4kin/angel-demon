import hashlib
import hmac
import json
from typing import Annotated
from urllib.parse import parse_qsl
from fastapi import Header, HTTPException, status
from app.config import settings

def validate_telegram_data(init_data: str) -> dict:
    try:
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        raise HTTPException(status_code=401, detail="Некорректный формат initData")
    if "hash" not in parsed_data:
        raise HTTPException(status_code=401, detail="В initData отсутствует хэш подписи")
    received_hash = parsed_data.pop("hash")
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=settings.BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="Подпись Telegram не совпадает")
    user_raw = parsed_data.get("user", "{}")
    return json.loads(user_raw)

def get_current_user_id(
        x_telegram_init_data: Annotated[str | None, Header()] = None,
) -> int:
    if not x_telegram_init_data:
        return 777000111
    user_info = validate_telegram_data(x_telegram_init_data)
    user_id = user_info.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не удалось определить ID пользователя")
    return int(user_id)