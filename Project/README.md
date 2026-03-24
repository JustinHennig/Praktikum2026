# Measurement App for SCPI Instruments

A Python desktop application for controlling and measuring data from electronic test equipment (oscilloscopes and function generators) via SCPI (Standard Commands for Programmable Instruments) over USB/VISA connections.

---

## Features

- **Dual-instrument support** — Control oscilloscopes (SDS series) and function generators (SDG series) simultaneously
- **Live measurements** — Capture frequency, amplitude, peak-to-peak voltage, and RMS values from the oscilloscope
- **Oscilloscope configuration** — Adjust V/div, T/div, offset, and trigger level; auto-set support
- **Function generator control** — Set waveform, frequency, amplitude, offset, and phase; toggle output on/off
- **Continuous measurements** — Single snapshot or periodic measurements over a configurable duration
- **Database persistence** — Save measurement sessions and configurations to a local SQLite database
- **Load & restore** — Reload saved configurations and measurement history from the database

---

## Project Structure

```
Project/
├── main.py                          # Application entry point
├── app/
│   ├── database/
│   │   ├── schema/
│   │   │   ├── 01_schema.sql        # Table definitions
│   │   │   └── 02_seed.sql          # Sample data
│   │   └── scripts/
│   │       ├── initialize.py        # Create schema + insert sample data
│   │       └── teardown.py          # Clear data (keeps schema)
│   ├── models/
│   │   └── measurement_record.py    # SQLAlchemy ORM models
│   ├── scpi_commands/
│   │   ├── device_independent_commands.py  # Device scanning & IDN
│   │   ├── sds_commands.py          # Oscilloscope (SDS) SCPI commands
│   │   └── sdg_commands.py          # Function generator (SDG) SCPI commands
│   ├── services/
│   │   └── device_worker.py         # Background thread worker for devices
│   ├── storage/
│   │   ├── sqlite_database.py       # Database access functions (SQLAlchemy)
│   │   └── csv_writer.py            # CSV export (not yet integrated)
│   └── ui/
│       ├── main_window.py           # Main window & application logic
│       └── components/
│           ├── connection_panel.py              # Device connection & scanning
│           ├── device_configure_panels.py       # Oscilloscope & generator configuration panels
│           ├── measurement_display.py           # Measurement data table
│           └── load_delete_measurement_window.py # Load/delete from database
└── data/
    └── database.db                  # SQLite database (auto-created)
```

---

## Requirements

- Python 3.10+
- [PySide6](https://pypi.org/project/PySide6/) — Qt GUI framework
- [PyVISA](https://pypi.org/project/PyVISA/) — SCPI instrument communication
- [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) — Database ORM

Install all dependencies:

```bash
pip install PySide6 pyvisa sqlalchemy
```

---

## Getting Started

### 1. Initialize the database

```bash
cd Project
python app/database/scripts/initialize.py
```

This creates the `data/database.db` file with the schema and optional sample data.

### 2. Run the application

```bash
python main.py
```

---

## Usage

1. **Connect a device** — Use the _Connection Panel_ to scan for connected VISA instruments.
2. **Select device type** — Choose between _Oscilloscope_ or _Function Generator_ from the dropdown.
3. **Configure** — Adjust settings in the configuration panel and apply them to the device.
4. **Measure** — Start a single or timed measurement; results appear in the table on the right.
5. **Save** — Save the current measurement session to the database via the display panel.
6. **Load** — Reload a previous session using the load/delete dialog.

---

## Architecture

```
UI Layer (PySide6)
    ↓
Services Layer (DeviceWorker threads)
    ↓
SCPI Commands Layer (sds_commands, sdg_commands)
    ↓
Hardware (Oscilloscope / Function Generator via PyVISA)
```

Device communication runs in **two dedicated background threads** (one per instrument type) using a queue-based task system. Results are sent back to the UI via Qt signals, keeping the interface responsive at all times.

---

## Database Schema

**`measurement_settings`** — One row per measurement session

| Column           | Type       | Description                     |
| ---------------- | ---------- | ------------------------------- |
| `measurement_id` | INTEGER PK | Auto-incremented ID             |
| `name`           | TEXT       | User-defined session name       |
| `device`         | TEXT       | VISA resource address           |
| `configuration`  | TEXT       | JSON — instrument configuration |

**`measurements`** — N rows per session

| Column               | Type       | Description                                           |
| -------------------- | ---------- | ----------------------------------------------------- |
| `id`                 | INTEGER PK | Auto-incremented ID                                   |
| `measurement_id`     | INTEGER FK | References `measurement_settings`                     |
| `time`               | TEXT       | ISO timestamp                                         |
| `measurement_values` | TEXT       | JSON — measured values (Frequency, Amplitude, RMS, …) |

The JSON fields are flexible and support arbitrary key-value pairs, so oscilloscope and generator data can share the same schema.

---

## Database Maintenance

```bash
# Reset data and re-insert sample records
python app/database/scripts/initialize.py

# Clear all measurement data (keeps schema intact)
python app/database/scripts/teardown.py
```
