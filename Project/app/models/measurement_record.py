from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class MeasurementSettings(Base):
    # Stores the configuration for a measurement session
    __tablename__ = "measurement_settings"

    measurement_id = Column(Integer, primary_key=True, autoincrement=True)
    device         = Column(String, nullable=False)
    configuration  = Column(String, nullable=False)

    measurements = relationship("Measurement", back_populates="settings")

class Measurement(Base):
    # Stores individual measurement entries linked to a MeasurementSettings record
    __tablename__ = "measurements"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    measurement_id     = Column(Integer, ForeignKey("measurement_settings.measurement_id"), nullable=False)
    time               = Column(String, nullable=False)
    measurement_values = Column(String, nullable=False)

    settings = relationship("MeasurementSettings", back_populates="measurements")