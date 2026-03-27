# This file defines the SQLAlchemy models for the measurement records, to avoid using raw SQL queries

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Measurement(Base):
    # Top-level measurement session
    __tablename__ = "measurement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    date_time: Mapped[str] = mapped_column(String, nullable=False)

    settings = relationship("MeasurementSetting", back_populates="measurement")

class MeasurementSetting(Base):
    # Stores the device configuration belonging to a measurement session
    __tablename__ = "measurement_setting"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_id: Mapped[int] = mapped_column(Integer, ForeignKey("measurement.id"), nullable=False)
    device: Mapped[str] = mapped_column(String, nullable=False)
    configuration: Mapped[str] = mapped_column(String, nullable=False)

    measurement = relationship("Measurement", back_populates="settings")
    values = relationship("MeasurementValue", back_populates="setting")

class MeasurementValue(Base):
    # Stores individual measurement data points linked to a MeasurementSetting
    __tablename__ = "measurement_value"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    measurement_setting_id: Mapped[int] = mapped_column(Integer, ForeignKey("measurement_setting.id"), nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)
    measurement_values: Mapped[str] = mapped_column(String, nullable=False)

    setting = relationship("MeasurementSetting", back_populates="values")
