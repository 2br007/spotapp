import pytest
import pytest_asyncio
import os
from httpx import AsyncClient
from fastapi.testclient import TestClient

os.environ.setdefault("db_dsn", "postgresql+asyncpg://user:pass@localhost_unittest:5432/mockup")
os.environ.setdefault("SECRET_KEY", "unit-test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")

import spotapp
from api.models import Base
from api.db import async_engine


@pytest.fixture
def client():
    """Client fixture"""

    with TestClient(spotapp.app) as client_fixture:
        yield client_fixture


@pytest_asyncio.fixture()
async def async_client():
    """Async client fixture"""

    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with AsyncClient(app=spotapp.app, base_url="http://test") as client_fixture:
        yield client_fixture

    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
