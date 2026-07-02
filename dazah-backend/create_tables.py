"""Directly create all 12 static_data tables in PostgreSQL"""
import pg8000

conn = pg8000.connect(user='postgres', password='postgres', database='dahzah', host='localhost', port=5432)
conn.autocommit = True
cursor = conn.cursor()

tables = [
    ("t_qs_storage_condition", """
        CREATE TABLE IF NOT EXISTS t_qs_storage_condition (
            id BIGSERIAL PRIMARY KEY,
            cond_code VARCHAR(50) NOT NULL,
            cond_name VARCHAR(100) NOT NULL,
            temp_min NUMERIC(5,2),
            temp_max NUMERIC(5,2),
            humidity VARCHAR(50),
            remark VARCHAR(500),
            status SMALLINT NOT NULL DEFAULT 0,
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_unit", """
        CREATE TABLE IF NOT EXISTS t_qs_unit (
            id BIGSERIAL PRIMARY KEY,
            unit_code VARCHAR(50) NOT NULL,
            unit_name VARCHAR(50) NOT NULL,
            unit_type VARCHAR(30) NOT NULL,
            base_value NUMERIC(20,6),
            remark VARCHAR(500),
            status SMALLINT NOT NULL DEFAULT 0,
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_test_item", """
        CREATE TABLE IF NOT EXISTS t_qs_test_item (
            id BIGSERIAL PRIMARY KEY,
            item_code VARCHAR(50) NOT NULL,
            item_name VARCHAR(100) NOT NULL,
            item_category VARCHAR(30) NOT NULL,
            unit_code VARCHAR(50) NOT NULL,
            method_desc VARCHAR(500),
            sort_num INTEGER DEFAULT 0,
            status SMALLINT NOT NULL DEFAULT 0,
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_equipment", """
        CREATE TABLE IF NOT EXISTS t_qs_equipment (
            id BIGSERIAL PRIMARY KEY,
            eq_code VARCHAR(50) NOT NULL,
            eq_name VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            serial_no VARCHAR(100) NOT NULL,
            manufacturer VARCHAR(100) NOT NULL,
            lab_id BIGINT NOT NULL,
            location VARCHAR(100) NOT NULL,
            eq_category VARCHAR(50) NOT NULL,
            cal_cycle INTEGER NOT NULL,
            last_cal_date DATE NOT NULL,
            next_cal_date DATE NOT NULL,
            verify_status VARCHAR(30) NOT NULL,
            eq_status SMALLINT NOT NULL DEFAULT 0,
            manager_id BIGINT NOT NULL,
            attach_file TEXT,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_chrom_column", """
        CREATE TABLE IF NOT EXISTS t_qs_chrom_column (
            id BIGSERIAL PRIMARY KEY,
            col_code VARCHAR(50) NOT NULL,
            col_type VARCHAR(50) NOT NULL,
            spec VARCHAR(100) NOT NULL,
            manufacturer VARCHAR(100) NOT NULL,
            serial_no VARCHAR(100) NOT NULL,
            purchase_date DATE NOT NULL,
            use_start_date DATE,
            max_use_times INTEGER NOT NULL,
            used_times INTEGER NOT NULL DEFAULT 0,
            storage_cond_code VARCHAR(50) NOT NULL,
            location VARCHAR(100) NOT NULL,
            col_status SMALLINT NOT NULL DEFAULT 0,
            apply_method VARCHAR(500),
            attach_file TEXT,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_medium", """
        CREATE TABLE IF NOT EXISTS t_qs_medium (
            id BIGSERIAL PRIMARY KEY,
            medium_code VARCHAR(50) NOT NULL,
            medium_name VARCHAR(100) NOT NULL,
            medium_type VARCHAR(50) NOT NULL,
            manufacturer VARCHAR(100) NOT NULL,
            batch_no VARCHAR(50) NOT NULL,
            spec VARCHAR(50) NOT NULL,
            storage_cond_code VARCHAR(50) NOT NULL,
            expire_date DATE NOT NULL,
            verify_status VARCHAR(30) NOT NULL,
            config_method TEXT,
            stock_num NUMERIC(20,4) NOT NULL DEFAULT 0,
            unit_code VARCHAR(50) NOT NULL,
            min_stock NUMERIC(20,4) NOT NULL,
            status SMALLINT NOT NULL DEFAULT 0,
            attach_file TEXT,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_reagent", """
        CREATE TABLE IF NOT EXISTS t_qs_reagent (
            id BIGSERIAL PRIMARY KEY,
            reagent_code VARCHAR(50) NOT NULL,
            reagent_name VARCHAR(100) NOT NULL,
            cas_no VARCHAR(50) NOT NULL,
            purity VARCHAR(30) NOT NULL,
            manufacturer VARCHAR(100) NOT NULL,
            batch_no VARCHAR(50) NOT NULL,
            spec VARCHAR(50) NOT NULL,
            danger_type VARCHAR(50) NOT NULL,
            storage_cond_code VARCHAR(50) NOT NULL,
            expire_date DATE NOT NULL,
            stock_num NUMERIC(20,4) NOT NULL,
            unit_code VARCHAR(50) NOT NULL,
            min_stock NUMERIC(20,4) NOT NULL,
            store_location VARCHAR(100) NOT NULL,
            attach_file TEXT,
            status SMALLINT NOT NULL DEFAULT 0,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_standard_material", """
        CREATE TABLE IF NOT EXISTS t_qs_standard_material (
            id BIGSERIAL PRIMARY KEY,
            std_code VARCHAR(50) NOT NULL,
            std_name VARCHAR(100) NOT NULL,
            cas_no VARCHAR(50),
            manufacturer VARCHAR(100) NOT NULL,
            batch_no VARCHAR(50) NOT NULL,
            cert_no VARCHAR(100) NOT NULL,
            purity NUMERIC(20,6) NOT NULL,
            init_stock NUMERIC(20,4) NOT NULL,
            remain_stock NUMERIC(20,4) NOT NULL,
            unit_code VARCHAR(50) NOT NULL,
            storage_cond_code VARCHAR(50) NOT NULL,
            expire_date DATE NOT NULL,
            store_location VARCHAR(100) NOT NULL,
            std_type VARCHAR(50) NOT NULL,
            recal_cycle INTEGER,
            min_stock NUMERIC(20,4) NOT NULL,
            attach_file TEXT,
            status SMALLINT NOT NULL,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_material_standard", """
        CREATE TABLE IF NOT EXISTS t_qs_material_standard (
            id BIGSERIAL PRIMARY KEY,
            material_code VARCHAR(50) NOT NULL,
            material_name VARCHAR(100) NOT NULL,
            material_type VARCHAR(50) NOT NULL,
            spec VARCHAR(100) NOT NULL,
            supplier_id BIGINT,
            standard_source VARCHAR(50) NOT NULL,
            standard_no VARCHAR(50) NOT NULL,
            version VARCHAR(20) NOT NULL,
            storage_cond_code VARCHAR(50) NOT NULL,
            status SMALLINT NOT NULL DEFAULT 0,
            draft_user BIGINT NOT NULL,
            audit_user BIGINT,
            approve_user BIGINT,
            effect_date DATE,
            invalid_date DATE,
            attach_file TEXT,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_material_standard_item", """
        CREATE TABLE IF NOT EXISTS t_qs_material_standard_item (
            id BIGSERIAL PRIMARY KEY,
            standard_id BIGINT NOT NULL,
            item_code VARCHAR(50) NOT NULL,
            test_method VARCHAR(500),
            limit_type VARCHAR(30) NOT NULL,
            limit_min NUMERIC(30,10),
            limit_max NUMERIC(30,10),
            is_release_item SMALLINT NOT NULL DEFAULT 0,
            sort_num INTEGER DEFAULT 0,
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_product_standard", """
        CREATE TABLE IF NOT EXISTS t_qs_product_standard (
            id BIGSERIAL PRIMARY KEY,
            product_code VARCHAR(50) NOT NULL,
            product_name VARCHAR(100) NOT NULL,
            trade_name VARCHAR(100),
            spec VARCHAR(100) NOT NULL,
            dosage_form VARCHAR(50) NOT NULL,
            reg_standard_no VARCHAR(100) NOT NULL,
            inner_standard_no VARCHAR(50) NOT NULL,
            version VARCHAR(20) NOT NULL,
            storage_cond_code VARCHAR(50) NOT NULL,
            valid_period INTEGER NOT NULL,
            pack_spec VARCHAR(100) NOT NULL,
            status SMALLINT NOT NULL DEFAULT 0,
            draft_user BIGINT NOT NULL,
            audit_user BIGINT,
            approve_user BIGINT,
            effect_date DATE,
            invalid_date DATE,
            attach_file TEXT,
            remark VARCHAR(500),
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            update_by BIGINT,
            update_time TIMESTAMP DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
    ("t_qs_product_standard_item", """
        CREATE TABLE IF NOT EXISTS t_qs_product_standard_item (
            id BIGSERIAL PRIMARY KEY,
            standard_id BIGINT NOT NULL,
            item_code VARCHAR(50) NOT NULL,
            test_method VARCHAR(500),
            legal_limit_min NUMERIC(30,10),
            legal_limit_max NUMERIC(30,10),
            inner_limit_min NUMERIC(30,10),
            inner_limit_max NUMERIC(30,10),
            is_release_item SMALLINT NOT NULL DEFAULT 0,
            sort_num INTEGER DEFAULT 0,
            create_by BIGINT NOT NULL,
            create_time TIMESTAMP NOT NULL DEFAULT NOW(),
            del_flag SMALLINT NOT NULL DEFAULT 0
        )"""),
]

for name, ddl in tables:
    try:
        cursor.execute(ddl)
        print(f"OK: {name}")
    except Exception as e:
        print(f"ERR: {name} -> {e}")

# Create indexes
indexes = [
    "CREATE INDEX IF NOT EXISTS ix_t_qs_storage_cond_code ON t_qs_storage_condition(cond_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_unit_code ON t_qs_unit(unit_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_test_item_code ON t_qs_test_item(item_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_equipment_code ON t_qs_equipment(eq_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_equipment_next_cal ON t_qs_equipment(next_cal_date)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_chrom_col_code ON t_qs_chrom_column(col_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_chrom_col_used_times ON t_qs_chrom_column(used_times)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_medium_code ON t_qs_medium(medium_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_medium_expire ON t_qs_medium(expire_date)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_reagent_code ON t_qs_reagent(reagent_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_reagent_expire ON t_qs_reagent(expire_date)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_std_mat_code ON t_qs_standard_material(std_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_std_mat_expire ON t_qs_standard_material(expire_date)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_mat_std_code ON t_qs_material_standard(material_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_mat_std_version ON t_qs_material_standard(material_code, version, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_mat_std_item_std_id ON t_qs_material_standard_item(standard_id)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_prod_std_code ON t_qs_product_standard(product_code, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_prod_std_version ON t_qs_product_standard(product_code, version, del_flag)",
    "CREATE INDEX IF NOT EXISTS ix_t_qs_prod_std_item_std_id ON t_qs_product_standard_item(standard_id)",
]

for idx_sql in indexes:
    try:
        cursor.execute(idx_sql)
        print(f"IDX OK: {idx_sql[:60]}...")
    except Exception as e:
        print(f"IDX ERR: {e}")

# Verify
cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 't_qs_%'")
print(f"\nTotal t_qs_* tables: {cursor.fetchone()[0]}")

cursor.close()
conn.close()