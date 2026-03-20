from pathlib import Path
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.measurement_record import MeasurementSettings
from app.models.measurement_record import Measurement

# Resolve the path to the 'data' directory three levels above this file (Project/data/)
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database.db"

# Create the SQLAlchemy engine connecting to the SQLite database file
engine = create_engine(f"sqlite:///{DB_PATH}")

Session = sessionmaker(bind=engine)

#Insert a new measurement configuration and return its generated ID.
def insert_measurement_settings(device: str, parameters: dict) -> int:
    with Session() as session:
        settings = MeasurementSettings(
            device=device,
            configuration=json.dumps(parameters),   # store dict as JSON string
        )
        session.add(settings)
        session.commit()
        return settings.measurement_id


#Insert a single measurement row linked to an existing measurement_settings record.
def insert_measurement(measurement_id: int, time: str, values: dict) -> int:
    with Session() as session:
        measurement = Measurement(
            measurement_id=measurement_id,
            time=time,
            measurement_values=json.dumps(values)  # store dict as JSON string
        )
        session.add(measurement)
        session.commit()
        return measurement.id
    
# Function to get all measurement settings for listing or loading purposes
def get_all_measurement_settings():
    with Session() as session:
        rows = session.query(MeasurementSettings).all()
        return [
            {
                "measurement_id": row.measurement_id,
                "device": row.device,
                "configuration": json.loads(row.configuration)  # convert JSON string back to dict
            }
            for row in rows
        ]

# Function to get all measurement entries for a specific measurement_id 
def get_measurements_by_id(measurement_id: int) -> dict:
    with Session() as session:
        rows = session.query(Measurement).filter(
            Measurement.measurement_id == measurement_id
        ).all()
        return [
            {
                "time":   r.time,
                "values": json.loads(r.measurement_values),
            }
            for r in rows
        ]