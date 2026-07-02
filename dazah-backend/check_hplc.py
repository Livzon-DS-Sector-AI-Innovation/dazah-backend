"""Check HPLC reference data"""
import asyncio
from app.core.database import get_db
from app.modules.quality.static_data.models import HplcReference
from sqlalchemy import select, text

async def check():
    async for db in get_db():
        # Check if table exists
        result = await db.execute(text("SELECT COUNT(*) FROM public.t_qs_hplc_reference"))
        count = result.scalar()
        print(f'Table has {count} rows')
        
        # Try to query using the model
        result2 = await db.execute(select(HplcReference).limit(3))
        items = list(result2.scalars().all())
        print(f'Model returned {len(items)} items')
        for item in items:
            print(f'  - {item.ref_code}: {item.ref_name}')
        break

asyncio.run(check())