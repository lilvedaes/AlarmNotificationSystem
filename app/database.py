from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Use the DATABASE_URL from settings, adjusted for asyncpg
DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

# Async engine setup
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Async sessionmaker setup
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()
