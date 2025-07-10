import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator

from src.main import app 
from src.settings import DATABASE_URL 
from src.database.db import get_db 

DATABASE_TEST_URL = f"{DATABASE_URL}_test"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_database():
    engine = create_async_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        database_name = DATABASE_TEST_URL.split("/")[-1]
        try:
            await conn.execute(text(f"CREATE DATABASE {database_name}"))
        except ProgrammingError:
            pass
    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def engine():
    db_engine = create_async_engine(DATABASE_TEST_URL)
    yield db_engine
    await db_engine.dispose()

@pytest.fixture(scope="session")
def async_session_factory(engine):
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(autouse=True)
async def clean_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

@pytest_asyncio.fixture
async def session(async_session_factory):
    async with async_session_factory() as db_session:
        yield db_session
        await db_session.rollback()

@pytest_asyncio.fixture
async def client(session: AsyncSession):
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
    
    del app.dependency_overrides[get_db]