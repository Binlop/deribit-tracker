import os
from types import SimpleNamespace

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine

from db.session import Base
from apps.prices.models import IndexPrice  # noqa: F401

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5433/deribit_test",
)

@pytest_asyncio.fixture(scope="session")
async def engine():
    assert "test" in TEST_DATABASE_URL, "TEST_DATABASE_URL должен указывать на тестовую БД"
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all())
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture()
async def session(engine: AsyncEngine):
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        yield session
        await session.close()
        await transaction.rollback()

@pytest_asyncio.fixture()
async def repository(session: AsyncSession):
    from apps.prices.repository import IndexPriceRepository
    uow = SimpleNamespace(db=session)
    return IndexPriceRepository(uow)