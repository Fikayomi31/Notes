import os

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from concurrent.interpreters import create

## Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./notes.db")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Async database engine
engine = create_async_engine(
    DATABASE_URL, 
    echo=True, 
    pool_pre_ping=True
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)

#Base class for all database models
class Base(DeclarativeBase):
    pass

# Deoendency to get the database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        