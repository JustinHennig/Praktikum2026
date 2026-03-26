# This file contains functions for interacting with the SQLite database using SQLAlchemy

from pathlib import Path
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.measurement_record import Measurement, MeasurementSetting, MeasurementValue

# Resolve the path to the 'data' directory three levels above this file (Project/data/)
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database.db"

# Create the SQLAlchemy engine connecting to the SQLite database file
engine = create_engine(f"sqlite:///{DB_PATH}")

Session = sessionmaker(bind=engine)

# Insert a new top-level measurement session and return its generated ID.
def insert_measurement(name: str, date_time: str) -> int:
    with Session() as session:
        measurement = Measurement(name=name, date_time=date_time)
        session.add(measurement)
        session.commit()
        return measurement.id

# Insert a measurement setting linked to a measurement session and return its generated ID.
def insert_measurement_setting(measurement_id: int, device: str, configuration: dict) -> int:
    with Session() as session:
        setting = MeasurementSetting(
            measurement_id=measurement_id,
            device=device,
            configuration=json.dumps(configuration),
        )
        session.add(setting)
        session.commit()
        return setting.id

# Insert a single measurement value row linked to a measurement setting.
def insert_measurement_value(measurement_setting_id: int, time: str, values: dict) -> int:
    with Session() as session:
        value = MeasurementValue(
            measurement_setting_id=measurement_setting_id,
            time=time,
            measurement_values=json.dumps(values),
        )
        session.add(value)
        session.commit()
        return value.id

# Return all measurement sessions with their settings for listing/loading purposes.
def get_all_measurements() -> list[dict]:
    with Session() as session:
        rows = session.query(Measurement).all()
        return [
            {
                "id": row.id,
                "name": row.name,
                "date_time": row.date_time,
                "settings": [
                    {
                        "id": s.id,
                        "device": s.device,
                        "configuration": json.loads(s.configuration),
                    }
                    for s in row.settings
                ],
            }
            for row in rows
        ]

# Return all measurement values for a given measurement_setting id.
def get_values_by_setting_id(setting_id: int) -> list[dict]:
    with Session() as session:
        rows = session.query(MeasurementValue).filter(
            MeasurementValue.measurement_setting_id == setting_id
        ).all()
        return [
            {
                "time": r.time,
                "values": json.loads(r.measurement_values),
            }
            for r in rows
        ]

# Delete a measurement session and all its linked settings and values.
def delete_measurement_by_id(measurement_id: int):
    with Session() as session:
        settings = session.query(MeasurementSetting).filter(
            MeasurementSetting.measurement_id == measurement_id
        ).all()
        for setting in settings:
            session.query(MeasurementValue).filter(
                MeasurementValue.measurement_setting_id == setting.id
            ).delete()
        session.query(MeasurementSetting).filter(
            MeasurementSetting.measurement_id == measurement_id
        ).delete()
        session.query(Measurement).filter(
            Measurement.id == measurement_id
        ).delete()
        session.commit()
