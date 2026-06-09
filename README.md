# Dahzah Backend

Backend service for the Dahzah factory system.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd dahzah-backend
```

### 2. Install dependencies

```bash
uv sync
```

This will:
- Create `.venv` virtual environment
- Install all dependencies from `pyproject.toml` including `openpyxl` for Excel processing

### 3. Configure environment variables

Copy the example environment file and update as needed:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests:

```bash
uv run pytest
```

## Key Features

### CPV Module (Continuous Process Validation)

- Product management (CRUD operations)
- CPP/CQA batch data import from Excel
- Data preview before import (supports create/update/overwrite modes)
- Batch data export to Excel
- Statistical analysis and trend visualization

#### Testing Excel Import Preview

```bash
# Test the preview endpoint
curl -X POST "http://localhost:8000/api/v1/quality/cpv/import/preview?product_id=<product-id>&data_type=CPP&import_mode=create" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.xlsx"
```

## Project Structure

```
.
├── app/
│   ├── api/              # API routes and dependencies
│   ├── core/             # Core configuration and utilities
│   ├── modules/          # Business logic modules
│   │   └── quality/      # Quality management (CPV)
│   │       ├── api/      # API endpoints
│   │       ├── service/  # Business logic
│   │       └── models/   # Database models
│   └── platform/         # Cross-cutting concerns
├── alembic/              # Database migrations
├── tests/                # Test suite
├── pyproject.toml        # Project dependencies
└── uv.lock              # Dependency lock file
```

## Dependencies

Key dependencies:
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM with async support
- **Alembic**: Database migrations
- **openpyxl**: Excel file processing
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

For a complete list, see `pyproject.toml`.

## Development

### Code Quality

```bash
# Run linter
uv run ruff check .

# Run type checker
uv run mypy .

# Format code
uv run ruff format .
```

### Adding New Dependencies

```bash
# Add a dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Remove a dependency
uv remove <package-name>
```

## License

[Your license information]
