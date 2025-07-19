import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

log = logging.getLogger(__name__)

# PostgreSQL connection URL (replace with your actual credentials)
DATABASE_URL = os.getenv("DATABASE_URL")


log = logging.getLogger(__name__)

# Async engine creation
# creates the engine in an asynchronous context for PostgreSQL using asyncpg.
# Manages async DB connections and pooling
engine = create_async_engine(DATABASE_URL, echo=True)

# Session maker with AsyncSession
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()
