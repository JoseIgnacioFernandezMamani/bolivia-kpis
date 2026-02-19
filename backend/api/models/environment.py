from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from geoalchemy2 import Geography
from database import Base
from models.base import TimestampMixin


class DeforestationZone(Base, TimestampMixin):
    __tablename__ = "deforestation_zones"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    area_ha = Column(Float, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    geometry = Column(Geography(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)


class ProtectedArea(Base, TimestampMixin):
    __tablename__ = "protected_areas"

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    category = Column(String(100), nullable=True)
    area_ha = Column(Float, nullable=True)
    geometry = Column(Geography(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)


class MiningConcession(Base, TimestampMixin):
    __tablename__ = "mining_concessions"

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=True)
    mineral = Column(String(100), nullable=True)
    company = Column(String(300), nullable=True)
    area_ha = Column(Float, nullable=True)
    geometry = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)


class LithiumSaltFlat(Base, TimestampMixin):
    __tablename__ = "lithium_salt_flats"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    estimated_reserves_mt = Column(Float, nullable=True)
    geometry = Column(Geography(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)


class CO2Emission(Base, TimestampMixin):
    __tablename__ = "co2_emissions"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    sector = Column(String(100), nullable=True)
    value_mt = Column(Float, nullable=False)


class ForestFire(Base, TimestampMixin):
    """NASA FIRMS active fire detections."""

    __tablename__ = "forest_fires"

    id = Column(Integer, primary_key=True)
    detected_date = Column(Date, nullable=False, index=True)
    confidence = Column(Integer, nullable=True)
    frp = Column(Float, nullable=True)  # Fire Radiative Power (MW)
    satellite = Column(String(50), nullable=True)
    geometry = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
