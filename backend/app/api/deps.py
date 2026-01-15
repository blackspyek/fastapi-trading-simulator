from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.db import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
        Dependency for getting async database session.
        Yields a database session and ensures it's closed after the request.
    """
    async with AsyncSessionLocal() as session:
        yield session