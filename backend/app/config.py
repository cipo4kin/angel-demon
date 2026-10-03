from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    DEBUG: bool = False
    BOT_TOKEN: str = ""
    GROQ_API_KEY: str = ""
    GROQ_API_KEYS: str = ""
    GROQ_MODEL: str = "qwen/qwen3.8-27b"
    DB_PATH: Path = Path(__file__).resolve().parent / "database" / "angel_demon.db"
    FRONTEND_DIR: Path = Path(__file__).resolve().parent.parent.parent / "frontend"
    WEBAPP_URL: str = ""
    PRICE_SKIN_GOPNIK: int = 50
    PRICE_SKIN_OFFICE: int = 50
    PRICE_JUDGE_PACK_3: int = 25

    @property
    def groq_keys(self) -> list[str]:
        keys: list[str] = []
        for src in (self.GROQ_API_KEYS, self.GROQ_API_KEY):
            if not src:
                continue
            for k in src.split(","):
                k_clean = k.strip()
                if k_clean and k_clean not in keys:
                    keys.append(k_clean)
        return keys


settings = Settings()