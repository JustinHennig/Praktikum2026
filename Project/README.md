# Measurement App for SCPI Instruments

A Python desktop application for controlling and measuring data from electronic test equipment (oscilloscopes and function generators) via SCPI (Standard Commands for Programmable Instruments) over USB/VISA connections.

---

## Features

- **Dual-instrument support** — Control oscilloscopes (SDS series) and function generators (SDG series) simultaneously
- **Live measurements** — Capture frequency, amplitude, peak-to-peak voltage, and RMS values from the oscilloscope
- **Oscilloscope configuration** — Adjust V/div, T/div, offset, and trigger level; auto-set support
- **Function generator control** — Set waveform, frequency, amplitude, offset, and phase; toggle channel output on/off
- **Multiple measurement modes:**
  - **Single** — One-shot measurement
  - **Period of time** — Periodic measurements over a configurable duration at a configurable rate
  - **Sweep** — Automated frequency sweep across a range, capturing amplitude, Pk-Pk, and RMS at each step
  - **Snapshot** — Full high-resolution waveform capture exported as a timestamped CSV
- **Waveform smoothing** — Optional Moving Average or Savitzky-Golay filter applied to snapshot data
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
│   │   │   ├── 02_load_mock_data.sql # Sample INSERT statements
│   │   │   └── 03_drop_tables.sql   # DROP tables + reset AUTOINCREMENT
│   │   └── scripts/
│   │       ├── initialize.py        # Create schema (runs 01_schema.sql)
│   │       ├── load_mock_data.py    # Insert sample data (runs 02_load_mock_data.sql)
│   │       └── teardown.py          # Drop all tables (runs 03_drop_tables.sql)
│   ├── models/
│   │   └── measurement_record.py    # SQLAlchemy ORM models
│   ├── resources/                   # Reserved for future assets
│   ├── scpi_commands/
│   │   ├── device_independent_commands.py  # Device scanning & IDN
│   │   ├── sds_commands.py          # Oscilloscope (SDS) SCPI commands
│   │   └── sdg_commands.py          # Function generator (SDG) SCPI commands
│   ├── services/
│   │   ├── device_worker.py         # Background thread task-queue worker
│   │   ├── single_measurement.py    # One-shot oscilloscope measurement
│   │   ├── period_of_time_measurements.py  # QTimer-based periodic measurements
│   │   ├── snapshot.py              # Full waveform capture + CSV export
│   │   └── sweep_measurement.py     # Frequency sweep across SDG + SDS
│   ├── storage/
│   │   ├── sqlite_database.py       # Database access functions (SQLAlchemy)
│   │   └── csv_writer.py            # CSV export helper (not yet integrated)
│   └── ui/
│       ├── main_window.py           # Main window & application logic
│       ├── styling/
│       │   └── theme.qss            # Qt stylesheet
│       └── components/
│           ├── connection_panel.py              # Device connection & scanning
│           ├── device_configure_panels.py       # Oscilloscope & generator configuration panels
│           ├── measurement_display.py           # Measurement data table + DB save/load
│           └── load_delete_measurement_window.py # Load/delete sessions from database
└── data/
    └── database.db                  # SQLite database (auto-created by initialize.py)
```

---

## Requirements

- Python 3.10+
- Some computer require to download the NI-VISA driver
- [PySide6](https://pypi.org/project/PySide6/) — Qt GUI framework
- [PyVISA](https://pypi.org/project/PyVISA/) — SCPI instrument communication
- [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) — Database ORM
- [NumPy](https://pypi.org/project/numpy/) — Waveform data processing
- [SciPy](https://pypi.org/project/scipy/) — Savitzky-Golay smoothing filter

Install all dependencies:

```bash
pip install PySide6 pyvisa sqlalchemy numpy scipy
```

---

## Getting Started

### 1. Initialize the database

```bash
cd Project
python app/database/scripts/initialize.py
```

This creates the `data/database.db` file with the full schema.

Optionally, load sample data:

```bash
python app/database/scripts/load_mock_data.py
```

### 2. Run the application

```bash
python main.py
```

---

## Usage

1. **Connect a device** — Use the _Connection Panel_ to scan for connected VISA instruments and select oscilloscope / generator resources.
2. **Configure the oscilloscope** — Adjust V/div, T/div, offset, and trigger level; use _Scan Current Settings_ to read live values from the device or _Auto Set_ for automatic configuration.
3. **Configure the function generator** — Set waveform type, frequency, amplitude, offset, and phase; toggle channel output on/off.
4. **Choose a measurement mode:**
   - **Snapshot** — Configure the number of points and an optional smoothing filter, then start the capture. The waveform is saved as a CSV in `data/`.
   - **Single** — Select which values to capture (Frequency, Amplitude, Pk-Pk, RMS) and take a one-shot reading.
   - **Period of time** — Set a duration (s) and measurement rate (measurements/s) for a continuous recording.
   - **Sweep** — Define a start/stop frequency and number of steps; the generator steps through the range while the oscilloscope records at each point.
5. **Save** — Click _Insert into Database_ in the results panel to persist the current session.
6. **Load** — Use _Load from Database_ to browse, restore, or delete previous sessions.

---

## Architecture

```
UI Layer (PySide6)
    |
Services Layer (DeviceWorker threads)
    |
SCPI Commands Layer (sds_commands, sdg_commands)
    |
Hardware (Oscilloscope / Function Generator via PyVISA)
```

Device communication runs in **dedicated background threads** using a queue-based task system (`DeviceWorker`). Results are sent back to the UI via Qt signals, keeping the interface responsive at all times. The connection panel has its own worker thread; the main window uses two additional threads — one for the oscilloscope and one for the function generator.

---

## Database Schema

**`measurement`** — One row per named measurement session

| Column      | Type       | Description                       |
| ----------- | ---------- | --------------------------------- |
| `id`        | INTEGER PK | Auto-incremented ID               |
| `name`      | TEXT       | User-defined session name         |
| `date_time` | TEXT       | ISO timestamp of session creation |

**`measurement_setting`** — One row per instrument configuration within a session

| Column           | Type       | Description                                                     |
| ---------------- | ---------- | --------------------------------------------------------------- |
| `id`             | INTEGER PK | Auto-incremented ID                                             |
| `measurement_id` | INTEGER FK | References `measurement`                                        |
| `device`         | TEXT       | VISA resource address                                           |
| `configuration`  | TEXT       | JSON — instrument configuration (channel, V/div, T/div, etc.)  |

**`measurement_value`** — N rows per setting, one per data point

| Column                   | Type       | Description                                           |
| ------------------------ | ---------- | ----------------------------------------------------- |
| `id`                     | INTEGER PK | Auto-incremented ID                                   |
| `measurement_setting_id` | INTEGER FK | References `measurement_setting`                      |
| `time`                   | TEXT       | ISO timestamp of the individual reading               |
| `measurement_values`     | TEXT       | JSON — measured values (Frequency, Amplitude, RMS, …) |

The JSON fields are flexible and support arbitrary key-value pairs, so oscilloscope and generator data share the same schema.

---

## Database Maintenance

```bash
# Create schema (safe to run on a fresh install)
python app/database/scripts/initialize.py

# Load sample/mock data
python app/database/scripts/load_mock_data.py

# Drop all tables and reset auto-increment counters
python app/database/scripts/teardown.py
```
