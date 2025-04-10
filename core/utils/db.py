import logging

import aiosqlite

logger = logging.getLogger(__name__)


async def create_users_db():
    async with aiosqlite.connect('core/databases/users.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                api_token TEXT
            )
        ''')
        logger.info('База успешно создана.')
        await db.commit()


async def check_user_token(user_id: int):
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        )
        user = await cursor.fetchone()
        return user


async def get_user_token(user_id: int):
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT api_token FROM users WHERE user_id = ?', (user_id,)
        )
        token = await cursor.fetchone()
        return token[0]


async def add_or_update_user(user_id: int, username: str, api_token: str):
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT * FROM users WHERE user_id = ?', (user_id,)
        )
        user = await cursor.fetchone()

        if user:
            await db.execute('''
                UPDATE users
                SET api_token = ?
                WHERE user_id = ?
            ''', (api_token, user_id))
        else:
            await db.execute('''
                INSERT INTO users (
                             user_id,
                             username,
                             api_token
                             )
                VALUES (?, ?, ?)
            ''', (user_id, username, api_token))
        logger.info(f'Пользователь {user_id}: @{username} был добавлен в базу')
        await db.commit()
