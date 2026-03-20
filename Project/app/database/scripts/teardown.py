"""
Clears all data from the database tables without dropping them.
The schema (table structure) is preserved — only the rows are deleted.
Usage: python teardown.py
"""

import sqlite3
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH    = SCRIPT_DIR / "../../../data/database.db"

# Tables to clear, in order to respect foreign key constraints
# (child table 'measurements' must be cleared before parent 'measurement_settings')
TABLES = ["measurements", "measurement_settings"]

if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH.resolve()}")
        raise SystemExit(1)

    print(f"Clearing data from: {DB_PATH.resolve()}")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for table in TABLES:
            conn.execute(f"DELETE FROM {table}")
            # Reset the AUTOINCREMENT counter so IDs start from 1 again
            conn.execute(f"DELETE FROM sqlite_sequence WHERE name = '{table}'")
            print(f"  Cleared: {table}")

    print("Done.")
