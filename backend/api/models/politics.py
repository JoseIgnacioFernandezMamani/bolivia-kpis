from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from database import Base
from models.base import TimestampMixin


class ElectionResult(Base, TimestampMixin):
    __tablename__ = "election_results"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    election_type = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    party = Column(String(200), nullable=True)
    candidate = Column(String(200), nullable=True)
    votes = Column(Integer, nullable=True)
    percentage = Column(Float, nullable=True)
    geometry = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)


class DemocracyIndex(Base, TimestampMixin):
    __tablename__ = "democracy_index"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    score = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)


class CorruptionIndex(Base, TimestampMixin):
    __tablename__ = "corruption_index"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    cpi_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=True)


class SocialConflict(Base, TimestampMixin):
    __tablename__ = "social_conflicts"

    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    geometry = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)


class TIOCTerritory(Base, TimestampMixin):
    __tablename__ = "tioc_territories"

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    ethnicity = Column(String(200), nullable=True)
    area_ha = Column(Float, nullable=True)
    geometry = Column(Geography(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)
