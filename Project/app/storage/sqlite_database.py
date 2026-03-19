
from pathlib import Path
import sqlite3
from typing import Any
import os

# Datenbank im Unterordner 'data' speichern
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "measurements.db"

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER NOT NULL,
                time TEXT NOT NULL,
                freq REAL,
                amplitude REAL,
                peak_to_peak REAL,
                rms REAL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS measurement_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                measurement_id INTEGER NOT NULL,
                v_div_mv REAL,
                t_div_ms REAL,
                offset_mv REAL,
                trigger_level REAL,
                FOREIGN KEY (measurement_id) REFERENCES measurements(id)
            )
        """)

def insert_measurement_into_db(
    time: str,
    freq: float | None,
    amplitude: float | None,
    peak_to_peak: float | None,
    rms: float | None,
    v_div_mv: float | None,
    t_div_ms: float | None,
    offset_mv: float | None,
    trigger_level: float | None,
) -> int:
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO measurements (time, freq, amplitude, peak_to_peak, rms)
            VALUES (?, ?, ?, ?, ?)
        """, (time, freq, amplitude, peak_to_peak, rms))

        measurement_id = cursor.lastrowid

        conn.execute("""
            INSERT INTO measurement_settings (
                measurement_id,
                v_div_mv,
                t_div_ms,
                offset_mv,
                trigger_level
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            measurement_id,
            v_div_mv,
            t_div_ms,
            offset_mv,
            trigger_level,
        ))

    return int(measurement_id)