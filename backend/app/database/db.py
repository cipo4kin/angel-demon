import asyncio
from collections.abc import AsyncGenerator
import aiosqlite
from app.config import settings

async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    db = await aiosqlite.connect(settings.DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()

async def init_db() -> None:
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(settings.DB_PATH) as db:
        await db.execute(
            """
CREATE TABLE IF NOT EXISTS users (
telegram_id INTEGER PRIMARY KEY,
karma_angel INTEGER NOT NULL DEFAULT 0,
karma_demon INTEGER NOT NULL DEFAULT 0,
judge_spheres INTEGER NOT NULL DEFAULT 1,
unlocked_skins TEXT NOT NULL DEFAULT '["classic"]'
);
"""
        )
        await db.execute(
            """
CREATE TABLE IF NOT EXISTS dilemmas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
text TEXT NOT NULL,
skin TEXT NOT NULL DEFAULT 'classic',
angel_answer TEXT NOT NULL,
demon_answer TEXT NOT NULL,
chosen_side TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(telegram_id)
);
"""
        )
        await db.commit()
async def main():
    print(f"Создаем базу: {settings.DB_PATH}")
    await init_db()
    print("Таблицы успешно созданы!")

    async with aiosqlite.connect(settings.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in await cursor.fetchall()]
        print(f"Таблицы на диске: {tables}")
if __name__ == "__main__":
    asyncio.run(main())
