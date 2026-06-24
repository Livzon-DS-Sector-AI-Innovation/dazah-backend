#!/usr/bin/env python3
"""Export FastAPI OpenAPI spec to openapi.json"""
import json
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

def main():
    spec = app.openapi()
    output_path = Path(__file__).parent.parent / "openapi.json"
    output_path.write_text(json.dumps(spec, indent=2))
    print(f"✓ OpenAPI spec exported to {output_path}")

if __name__ == "__main__":
    main()
