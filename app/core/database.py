from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.shared.module_registry import BUSINESS_SCHEMAS

settings = get_settings()

_search_path = "public,identity,core," + ",".join(BUSINESS_SCHEMAS)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    # 禁用 asyncpg prepared statement 缓存，避免表结构变更后报错
    # 参考: https://github.com/MagicStack/asyncpg/issues/736
    connect_args={
        "server_settings": {"search_path": _search_path},
        "statement_cache_size": 0,  # 禁用 prepared statement 缓存
        "max_cached_statement_lifetime": 0,  # 不缓存 statement
    },
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
