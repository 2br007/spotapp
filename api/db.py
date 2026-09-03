from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from api import models

from api.settings import settings


async_engine = create_async_engine(
    settings.db_dsn,
    pool_pre_ping=True,
    connect_args={"timeout": settings.db_query_timeout}
)

SessionFactory = sessionmaker(autoflush=False,
                              bind=async_engine,
                              class_=AsyncSession)


async def get_session() -> AsyncSession:
    """Session factory"""

    async with SessionFactory() as session:
        async with session.begin():
            yield session
            await session.commit()
