from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db


async def database_session_depends() -> AsyncGenerator[AsyncSession, None]:
    yield get_db