from sqlalchemy import Column, Integer, String, Float, ForeignKey
from geoalchemy2 import Geography
from database import Base
from models.base import TimestampMixin


class InternetPenetration(Base, TimestampMixin):
    __tablename__ = "internet_penetration"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    percentage = Column(Float, nullable=False)
    fixed_broadband_per_100 = Column(Float, nullable=True)
    mobile_per_100 = Column(Float, nullable=True)


class CoverageZone(Base, TimestampMixin):
    """4G/5G coverage polygon."""

    __tablename__ = "coverage_zones"

    id = Column(Integer, primary_key=True)
    operator = Column(String(100), nullable=True)
    technology = Column(String(10), nullable=False)  # 4G, 5G
    geometry = Column(Geography(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)


class RDSpending(Base, TimestampMixin):
    __tablename__ = "rd_spending"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    percentage_of_gdp = Column(Float, nullable=True)
    amount_usd = Column(Float, nullable=True)


class DigitalLiteracy(Base, TimestampMixin):
    __tablename__ = "digital_literacy"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    rate = Column(Float, nullable=False)
    age_group = Column(String(50), nullable=True)
