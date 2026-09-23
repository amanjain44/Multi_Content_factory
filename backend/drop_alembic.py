import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def drop_alembic():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    await engine.dispose()
    print("Dropped alembic_version table successfully.")

if __name__ == "__main__":
    asyncio.run(drop_alembic())
