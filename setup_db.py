from __future__ import annotations

"""Initialize and seed the local warehouse database.

This script is intentionally lightweight so it can be used both in local
development and in quick-start instructions.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from nl2sql.db.setup import initialize_database


def main() -> None:
    """Create schema and sample data using DATABASE_URL from the environment."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")
    initialize_database(database_url=database_url)
    print(f"Database initialized at {database_url}")


if __name__ == "__main__":
    main()
