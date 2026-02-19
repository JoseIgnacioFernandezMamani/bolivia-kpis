from sqlalchemy import Column, Integer, String, Float, ForeignKey
from geoalchemy2 import Geography
from database import Base
from models.base import TimestampMixin


class HDIIndex(Base, TimestampMixin):
    __tablename__ = "hdi_index"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    municipality = Column(String(200), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    hdi_score = Column(Float, nullable=False)
    geometry = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)


class LifeExpectancy(Base, TimestampMixin):
    __tablename__ = "life_expectancy"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    years = Column(Float, nullable=False)
    gender = Column(String(10), nullable=True)


class NutritionIndicator(Base, TimestampMixin):
    __tablename__ = "nutrition_indicators"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    chronic_malnutrition_rate = Column(Float, nullable=True)
    acute_malnutrition_rate = Column(Float, nullable=True)


class CensusData(Base, TimestampMixin):
    __tablename__ = "census_data"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    total_population = Column(Integer, nullable=True)
    urban_population = Column(Integer, nullable=True)
    rural_population = Column(Integer, nullable=True)
    literacy_rate = Column(Float, nullable=True)


class GenderGapIndex(Base, TimestampMixin):
    __tablename__ = "gender_gap_index"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    overall_score = Column(Float, nullable=True)
    economic_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    health_score = Column(Float, nullable=True)
    political_score = Column(Float, nullable=True)


class BasicServices(Base, TimestampMixin):
    __tablename__ = "basic_services"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    water_access_rate = Column(Float, nullable=True)
    sanitation_rate = Column(Float, nullable=True)
    electricity_rate = Column(Float, nullable=True)
    gas_rate = Column(Float, nullable=True)
