from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from database import Base
from models.base import TimestampMixin


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=True)
    geometry = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)
    geom_simplified = Column(Geography(geometry_type="POLYGON", srid=4326), nullable=True)

    gdp_records = relationship("GDPPerCapita", back_populates="department")
    unemployment_records = relationship("Unemployment", back_populates="department")
    contracts = relationship("PublicContract", back_populates="department")


class GDPPerCapita(Base, TimestampMixin):
    __tablename__ = "gdp_per_capita"

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    year = Column(Integer, nullable=False, index=True)
    value_usd = Column(Float, nullable=False)

    department = relationship("Department", back_populates="gdp_records")


class Inflation(Base, TimestampMixin):
    __tablename__ = "inflation"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=True)
    rate = Column(Float, nullable=False)


class Unemployment(Base, TimestampMixin):
    __tablename__ = "unemployment"

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    year = Column(Integer, nullable=False, index=True)
    rate = Column(Float, nullable=False)

    department = relationship("Department", back_populates="unemployment_records")


class Export(Base, TimestampMixin):
    __tablename__ = "exports"

    id = Column(Integer, primary_key=True)
    product = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    value_usd = Column(BigInteger, nullable=False)
    percentage_of_total = Column(Float, nullable=True)


class PublicContract(Base, TimestampMixin):
    __tablename__ = "public_contracts"

    id = Column(Integer, primary_key=True)
    title = Column(String(512), nullable=False)
    amount = Column(Float, nullable=True)
    contractor = Column(String(255), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    geometry = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    date = Column(Date, nullable=True)
    sicoes_id = Column(String(100), nullable=True, unique=True)

    department = relationship("Department", back_populates="contracts")
