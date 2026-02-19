from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from geoalchemy2 import Geography
from database import Base
from models.base import TimestampMixin


class CrimeRate(Base, TimestampMixin):
    __tablename__ = "crime_rates"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    crime_type = Column(String(200), nullable=True)
    count = Column(Integer, nullable=True)
    rate_per_100k = Column(Float, nullable=True)


class DrugSeizure(Base, TimestampMixin):
    """FELCN drug seizure point data."""

    __tablename__ = "drug_seizures"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=True, index=True)
    drug_type = Column(String(100), nullable=True)
    quantity_kg = Column(Float, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    geometry = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)


class RoadSegment(Base, TimestampMixin):
    __tablename__ = "road_segments"

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=True)
    road_type = Column(String(50), nullable=True)
    condition = Column(String(50), nullable=True)
    length_km = Column(Float, nullable=True)
    geometry = Column(Geography(geometry_type="LINESTRING", srid=4326), nullable=True)


class Prison(Base, TimestampMixin):
    __tablename__ = "prisons"

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    capacity = Column(Integer, nullable=True)
    population = Column(Integer, nullable=True)
    geometry = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)


class HealthcareFacility(Base, TimestampMixin):
    __tablename__ = "healthcare_facilities"

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    facility_type = Column(String(100), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    beds = Column(Integer, nullable=True)
    geometry = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
