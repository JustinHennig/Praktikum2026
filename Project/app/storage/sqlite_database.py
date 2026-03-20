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