"""
数据库迁移脚本：为 HplcReference 表添加精细库存管理字段，并创建领用记录表
执行方式：python migrations/add_hplc_reference_usage_fields.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def migrate():
    """执行迁移"""
    async with engine.begin() as conn:
        print("开始迁移...")
        
        # 检查表所在的 schema
        result = await conn.execute(text("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_name = 't_qs_hplc_reference'
        """))
        table_info = result.fetchone()
        
        if table_info:
            schema = table_info[0]
            print(f"找到表 t_qs_hplc_reference 在 schema: {schema}")
        else:
            schema = 'qms'
            print(f"表 t_qs_hplc_reference 不存在，将使用 schema: {schema}")
        
        table_prefix = f"{schema}.t_qs_hplc_reference"
        usage_table_prefix = f"{schema}.t_qs_hplc_reference_usage"

        # 1. 为 t_qs_hplc_reference 表添加新字段
        print("添加 HplcReference 新字段...")
        
        # 先添加字段
        alter_fields = [
            f"ALTER TABLE {table_prefix} ADD COLUMN IF NOT EXISTS spec_unit VARCHAR(10)",
            f"ALTER TABLE {table_prefix} ADD COLUMN IF NOT EXISTS total_amount NUMERIC(10,2)",
            f"ALTER TABLE {table_prefix} ADD COLUMN IF NOT EXISTS remaining_amount NUMERIC(10,2)",
            f"ALTER TABLE {table_prefix} ADD COLUMN IF NOT EXISTS remaining_unit VARCHAR(10) DEFAULT 'mg'",
            f"ALTER TABLE {table_prefix} ADD COLUMN IF NOT EXISTS recal_threshold NUMERIC(10,2)",
            f"ALTER TABLE {table_prefix} ADD COLUMN IF NOT EXISTS need_recal BOOLEAN DEFAULT FALSE",
        ]

        for sql in alter_fields:
            try:
                await conn.execute(text(sql))
                field_name = sql.split('ADD COLUMN IF NOT EXISTS')[1].strip().split()[0]
                print(f"  ✓ {field_name}")
            except Exception as e:
                err_msg = str(e)
                if 'already exists' in err_msg.lower() or 'duplicate' in err_msg.lower():
                    field_name = sql.split('ADD COLUMN IF NOT EXISTS')[1].strip().split()[0]
                    print(f"  ✓ {field_name} (已存在)")
                else:
                    print(f"  ⚠ 错误: {err_msg[:100]}")

        # 添加字段注释（PostgreSQL 使用 COMMENT ON COLUMN）
        comments = [
            f"COMMENT ON COLUMN {table_prefix}.spec_unit IS 'Specification unit (mg/g)'",
            f"COMMENT ON COLUMN {table_prefix}.total_amount IS 'Total amount (mg/g)'",
            f"COMMENT ON COLUMN {table_prefix}.remaining_amount IS 'Remaining amount (mg/g)'",
            f"COMMENT ON COLUMN {table_prefix}.remaining_unit IS 'Remaining amount unit'",
            f"COMMENT ON COLUMN {table_prefix}.recal_threshold IS 'Recalibration threshold (mg/g)'",
            f"COMMENT ON COLUMN {table_prefix}.need_recal IS 'Need recalibration flag'",
        ]
        
        for sql in comments:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass

        # 2. 创建领用记录表
        print("创建领用记录表 t_qs_hplc_reference_usage...")
        create_usage_table = f"""
        CREATE TABLE IF NOT EXISTS {usage_table_prefix} (
            id BIGSERIAL PRIMARY KEY,
            ref_id BIGINT NOT NULL,
            ref_code VARCHAR(50) NOT NULL,
            ref_name VARCHAR(200) NOT NULL,
            usage_amount NUMERIC(10,2) NOT NULL,
            usage_unit VARCHAR(10) DEFAULT 'mg',
            remaining_after NUMERIC(10,2),
            usage_person VARCHAR(100),
            usage_purpose VARCHAR(200),
            usage_date DATE DEFAULT CURRENT_DATE,
            remark TEXT,
            create_by INTEGER DEFAULT 0,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            del_flag INTEGER DEFAULT 0
        );
        """

        try:
            await conn.execute(text(create_usage_table))
            print("  ✓ t_qs_hplc_reference_usage 表创建成功")
            
            # 添加表注释
            await conn.execute(text(f"COMMENT ON TABLE {usage_table_prefix} IS 'HPLC Reference Substance Usage Log'"))
            
            # 添加字段注释
            usage_comments = [
                f"COMMENT ON COLUMN {usage_table_prefix}.ref_id IS 'Reference substance ID'",
                f"COMMENT ON COLUMN {usage_table_prefix}.ref_code IS 'Reference code'",
                f"COMMENT ON COLUMN {usage_table_prefix}.ref_name IS 'Reference name'",
                f"COMMENT ON COLUMN {usage_table_prefix}.usage_amount IS 'Usage amount (mg/g)'",
                f"COMMENT ON COLUMN {usage_table_prefix}.usage_unit IS 'Usage unit'",
                f"COMMENT ON COLUMN {usage_table_prefix}.remaining_after IS 'Remaining amount after usage'",
                f"COMMENT ON COLUMN {usage_table_prefix}.usage_person IS 'Person who used'",
                f"COMMENT ON COLUMN {usage_table_prefix}.usage_purpose IS 'Usage purpose/project'",
                f"COMMENT ON COLUMN {usage_table_prefix}.usage_date IS 'Usage date'",
                f"COMMENT ON COLUMN {usage_table_prefix}.create_by IS 'Creator'",
                f"COMMENT ON COLUMN {usage_table_prefix}.create_time IS 'Create time'",
                f"COMMENT ON COLUMN {usage_table_prefix}.del_flag IS 'Delete flag'",
            ]
            for cmt in usage_comments:
                try:
                    await conn.execute(text(cmt))
                except Exception:
                    pass
                    
        except Exception as e:
            err_msg = str(e)
            if 'already exists' in err_msg.lower():
                print("  ✓ t_qs_hplc_reference_usage 表已存在")
            else:
                print(f"  ⚠ 错误: {err_msg[:100]}")

        # 3. 为新表添加索引
        print("添加索引...")
        indexes = [
            f"CREATE INDEX IF NOT EXISTS idx_hplc_usage_ref_id ON {usage_table_prefix}(ref_id)",
            f"CREATE INDEX IF NOT EXISTS idx_hplc_usage_date ON {usage_table_prefix}(usage_date)",
            f"CREATE INDEX IF NOT EXISTS idx_hplc_need_recal ON {table_prefix}(need_recal)",
        ]

        for sql in indexes:
            try:
                await conn.execute(text(sql))
                print(f"  ✓ 索引创建成功")
            except Exception as e:
                err_msg = str(e)
                if 'already exists' in err_msg.lower():
                    print(f"  ✓ 索引已存在")
                else:
                    print(f"  ⚠ 错误: {err_msg[:100]}")

        print("迁移完成！")


if __name__ == "__main__":
    asyncio.run(migrate())