#!/bin/bash
set -e

echo "========================================"
echo "  Database Initialization"
echo "========================================"

# Wait for PostgreSQL to be ready
until pg_isready -h localhost -p 5432 -U postgres; do
  echo "Waiting for database..."
  sleep 2
done

# Create database if not exists
psql -h localhost -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'dazah'" | grep -q 1 || \
  psql -h localhost -U postgres -c "CREATE DATABASE dazah"

# Run migrations (creates schemas + tables)
cd /app/backend
uv run alembic upgrade head

# ── Bridge schema gaps ──
# Some ORM columns have no corresponding Alembic migration.
# This block ensures the DB matches the current ORM models.
echo "Ensuring schema consistency..."
psql -h localhost -U postgres -d dazah <<'SQL'
DO $$
BEGIN
  -- hr.departments
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='departments' AND column_name='is_production') THEN
    ALTER TABLE hr.departments ADD COLUMN is_production boolean NOT NULL DEFAULT false;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='departments' AND column_name='production_start_time') THEN
    ALTER TABLE hr.departments ADD COLUMN production_start_time varchar(8);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='departments' AND column_name='production_end_time') THEN
    ALTER TABLE hr.departments ADD COLUMN production_end_time varchar(8);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='departments' AND column_name='sort_order') THEN
    ALTER TABLE hr.departments ADD COLUMN sort_order integer NOT NULL DEFAULT 0;
  END IF;

  -- hr.employees
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='employees' AND column_name='position_level') THEN
    ALTER TABLE hr.employees ADD COLUMN position_level varchar(32);
  END IF;

  -- hr.training_ledgers (columns added after initial migration)
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='training_ledgers' AND column_name='ledger_type') THEN
    ALTER TABLE hr.training_ledgers ADD COLUMN ledger_type varchar(16) NOT NULL DEFAULT 'event';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='training_ledgers' AND column_name='department') THEN
    ALTER TABLE hr.training_ledgers ADD COLUMN department varchar(64);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='training_ledgers' AND column_name='training_time_start') THEN
    ALTER TABLE hr.training_ledgers ADD COLUMN training_time_start varchar(8);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='training_ledgers' AND column_name='training_time_end') THEN
    ALTER TABLE hr.training_ledgers ADD COLUMN training_time_end varchar(8);
  END IF;

  -- hr.training_ledger_pages
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='hr' AND table_name='training_ledger_pages' AND column_name='ledger_type') THEN
    ALTER TABLE hr.training_ledger_pages ADD COLUMN ledger_type varchar(32);
  END IF;
  -- fix: fill null ledger_type on training_ledger_pages (columns added after rows existed)
  UPDATE hr.training_ledger_pages SET ledger_type = 'event' WHERE ledger_type IS NULL;
  UPDATE hr.training_ledgers SET ledger_type = 'event' WHERE ledger_type IS NULL;
END
$$;
SQL

# Import dump.sql only if hr.employees table has no data
EMP_COUNT=$(psql -h localhost -U postgres -d dazah -tc "SELECT COUNT(*) FROM hr.employees" 2>/dev/null | xargs || echo "0")
if [ "$EMP_COUNT" = "0" ] && [ -f /app/backend/dump.sql ]; then
  echo "Importing existing data from dump.sql..."
  psql -h localhost -U postgres -d dazah < /app/backend/dump.sql
  echo "Data import complete."
else
  echo "Database already has data ($EMP_COUNT employees), skipping import."
fi

# Run seed data (idempotent, supplements departments/teams basic data)
uv run python scripts/seed.py

echo "Database initialization complete."
