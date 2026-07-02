"""检查表是否存在"""
import asyncio
from app.core.database import async_session_factory
from sqlalchemy import text

async def check():
    async with async_session_factory() as db:
        result = await db.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name = 't_qs_hplc_reference'
        """))
        rows = result.fetchall()
        print('Tables found:', rows)

asyncio.run(check())