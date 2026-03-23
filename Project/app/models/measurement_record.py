# This file defines the SQLAlchemy models for the measurement records, to avoid using raw SQL queries

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class MeasurementSettings(Base):
    # Stores the configuration for a measurement session
    __tablename__ = "measurement_settings"

    measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    configuration: Mapped[str] = mapped_column(String, nullable=False)

    measurements = relationship("Measurement", back_populates="settings")

class Measurement(Base):
    # Stores individual measurement entries linked to a MeasurementSettings record
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[int] = mapped_column(Integer, ForeignKey("measurement_settings.measurement_id"), nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)
    measurement_values: Mapped[str] = mapped_column(String, nullable=False)

    settings = relationship("MeasurementSettings", back_populates="measurements")