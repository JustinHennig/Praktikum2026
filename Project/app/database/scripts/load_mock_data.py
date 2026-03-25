# Inserts sample/mock data into the database.
# Run initialize.py first to ensure the schema exists.

import sqlite3
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH    = SCRIPT_DIR / "../../../data/database.db"
SCHEMA_DIR = SCRIPT_DIR / "../schema"

def run_sql_file(conn: sqlite3.Connection, path: Path):
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)
    print(f"  Executed: {path.name}")

if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH.resolve()}")
        print("Run initialize.py first to create the schema.")
        raise SystemExit(1)

    print(f"Loading mock data into: {DB_PATH.resolve()}")

    with sqlite3.connect(DB_PATH) as conn:
        run_sql_file(conn, SCHEMA_DIR / "02_load_mock_data.sql")

    print("Done.")