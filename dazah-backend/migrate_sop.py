import asyncio
import asyncpg

async def migrate():
    try:
        conn = await asyncpg.connect(
            host='127.0.0.1',
            user='postgres',
            password='postgres',
            database='dazah'
        )
        await conn.execute('''
            ALTER TABLE quality.sop_rule
            ADD COLUMN IF NOT EXISTS sop_file_path VARCHAR(512)
        ''')
        print('Column sop_file_path added successfully!')
        await conn.close()
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(migrate())
