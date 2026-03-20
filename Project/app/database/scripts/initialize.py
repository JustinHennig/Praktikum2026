"""
Initialisiert die SQLite-Datenbank anhand der SQL-Dateien im 'scheme'-Ordner.
Verwendung: python initialize.py
"""

import sqlite3
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH    = SCRIPT_DIR / "../../../data/database.db"
SCHEME_DIR = SCRIPT_DIR / "../scheme"

def run_sql_file(conn: sqlite3.Connection, path: Path):
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)
    print(f"  Ausgeführt: {path.name}")

if __name__ == "__main__":
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Initialisiere Datenbank: {DB_PATH.resolve()}")

    with sqlite3.connect(DB_PATH) as conn:
        run_sql_file(conn, SCHEME_DIR / "01_scheme.sql")
        run_sql_file(conn, SCHEME_DIR / "02_seed.sql")

    print("Fertig.")
