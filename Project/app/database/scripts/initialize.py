# Script to initialize the database

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
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initializing database: {DB_PATH.resolve()}")

    with sqlite3.connect(DB_PATH) as conn:
        run_sql_file(conn, SCHEMA_DIR / "01_schema.sql")
        run_sql_file(conn, SCHEMA_DIR / "02_seed.sql")

    print("Done.")
