import json
import aiosqlite

async def get_or_create_user(db: aiosqlite.Connection, telegram_id: int) -> dict:
    cursor = await db.execute(
        "SELECT * FROM users WHERE telegram_id = ?;",
        (telegram_id,)
    )
    user = await cursor.fetchone()
    if not user:
        await db.execute(
            "INSERT INTO users (telegram_id) VALUES (?);",
            (telegram_id,)
        )
        await db.commit()
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?;",
            (telegram_id,)
        )
        user = await cursor.fetchone()

    user_dict = dict(user)
    user_dict["unlocked_skins"] = json.loads(user_dict["unlocked_skins"])
    return user_dict
async def save_dilemma(
        db: aiosqlite.Connection,
        user_id: int,
        text: str,
        skin: str,
        angel_answer: str,
        demon_answer: str,
) -> int:
    cursor = await db.execute(
        """
INSERT INTO dilemmas (user_id, text, skin, angel_answer, demon_answer)
VALUES (?,?,?,?,?);""",
(user_id, text, skin, angel_answer, demon_answer),
    )
    await db.commit()
    return cursor.lastrowid
async def choose_side(
    db: aiosqlite.Connection,
    dilemma_id: int,
    user_id: int,
    side: str,
) -> dict:
    cursor = await db.execute(
        "UPDATE dilemmas SET chosen_side = ? WHERE id = ? AND user_id = ? AND chosen_side IS NULL;",
        (side, dilemma_id, user_id),
    )
    if cursor.rowcount > 0:
        if side == "angel":
            await db.execute(
                "UPDATE users SET karma_angel = karma_angel + 1 WHERE telegram_id = ?;",
                (user_id,),
            )
        elif side == "demon":
            await db.execute(
                "UPDATE users SET karma_demon = karma_demon + 1 WHERE telegram_id = ?;",
                (user_id,),
            )
        await db.commit()

    cursor = await db.execute(
        "SELECT karma_angel, karma_demon FROM users WHERE telegram_id = ?;",
        (user_id,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else {"karma_angel": 0, "karma_demon": 0}
async def get_user_history(
        db: aiosqlite.Connection,
        user_id: int,
        limit: int = 15,
) -> list[dict]:
    cursor = await db.execute(
        """
SELECT id, text, skin, angel_answer, demon_answer, chosen_side, created_at FROM dilemmas
WHERE user_id = ?
ORDER BY id DESC
LIMIT ?;""",
(user_id, limit),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
async def spend_judge_sphere(
        db: aiosqlite.Connection,
        user_id: int 
) -> bool:
    cursor = await db.execute(
        "SELECT judge_spheres FROM users WHERE telegram_id = ?;",
        (user_id,),
    )
    row = await cursor.fetchone()
    if not row or row["judge_spheres"] < 1:
        return False
    await db.execute(
        "UPDATE users SET judge_spheres = judge_spheres - 1 WHERE telegram_id = ?;",
        (user_id,),
    )
    await db.commit()
    return True
async def add_judge_spheres(
        db: aiosqlite.Connection,
        user_id: int,
        count: int,
) -> int:
    await get_or_create_user(db, user_id)
    await db.execute(
        "UPDATE users SET judge_spheres = judge_spheres + ? WHERE telegram_id = ?;",
        (count, user_id,),
    )
    await db.commit()

    cursor = await db.execute(
        "SELECT judge_spheres FROM users WHERE telegram_id = ?;",
        (user_id,),
    )
    row = await cursor.fetchone()
    return row["judge_spheres"] if row else count
async def unlock_skin(
        db: aiosqlite.Connection,
        user_id: int,
        skin_name: str,
) -> list[str]:
    user = await get_or_create_user(db, user_id)
    skins = user["unlocked_skins"]

    if skin_name not in skins:
        skins.append(skin_name)
        await db.execute(
            "UPDATE users SET unlocked_skins = ? WHERE telegram_id = ?;",
            (json.dumps(skins), user_id),
        )
        await db.commit()
    return skins

