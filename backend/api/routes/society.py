from typing import Optional
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_AsGeoJSON

from database import get_db
from models.society import HDIIndex, LifeExpectancy, NutritionIndicator, CensusData, GenderGapIndex, BasicServices
from schemas.common import GeoJSONFeatureCollection

router = APIRouter()


@router.get("/hdi")
async def hdi(
    year: Optional[int] = None,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(HDIIndex)
    if year:
        stmt = stmt.where(HDIIndex.year == year)
    if department_id:
        stmt = stmt.where(HDIIndex.department_id == department_id)
    result = await db.execute(stmt.order_by(HDIIndex.year))
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "year": r.year,
            "municipality": r.municipality,
            "department_id": r.department_id,
            "hdi_score": r.hdi_score,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/hdi/geojson", response_model=GeoJSONFeatureCollection)
async def hdi_geojson(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        HDIIndex.id,
        HDIIndex.year,
        HDIIndex.municipality,
        HDIIndex.hdi_score,
        ST_AsGeoJSON(HDIIndex.geometry).label("geom"),
    ).where(HDIIndex.geometry.isnot(None))
    if year:
        stmt = stmt.where(HDIIndex.year == year)
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "year": r.year,
                "municipality": r.municipality,
                "hdi_score": r.hdi_score,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/life-expectancy")
async def life_expectancy(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(LifeExpectancy)
    if year:
        stmt = stmt.where(LifeExpectancy.year == year)
    result = await db.execute(stmt.order_by(LifeExpectancy.year))
    records = result.scalars().all()
    return [
        {
            "year": r.year,
            "department_id": r.department_id,
            "years": r.years,
            "gender": r.gender,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/census")
async def census(
    year: Optional[int] = None,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CensusData)
    if year:
        stmt = stmt.where(CensusData.year == year)
    if department_id:
        stmt = stmt.where(CensusData.department_id == department_id)
    result = await db.execute(stmt.order_by(CensusData.year))
    records = result.scalars().all()
    return [
        {
            "year": r.year,
            "department_id": r.department_id,
            "total_population": r.total_population,
            "urban_population": r.urban_population,
            "rural_population": r.rural_population,
            "literacy_rate": r.literacy_rate,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/gender-gap")
async def gender_gap(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GenderGapIndex).order_by(GenderGapIndex.year))
    records = result.scalars().all()
    return [
        {
            "year": r.year,
            "overall_score": r.overall_score,
            "economic_score": r.economic_score,
            "education_score": r.education_score,
            "health_score": r.health_score,
            "political_score": r.political_score,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/basic-services")
async def basic_services(
    year: Optional[int] = None,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BasicServices)
    if year:
        stmt = stmt.where(BasicServices.year == year)
    if department_id:
        stmt = stmt.where(BasicServices.department_id == department_id)
    result = await db.execute(stmt.order_by(BasicServices.year))
    records = result.scalars().all()
    return [
        {
            "year": r.year,
            "department_id": r.department_id,
            "water_access_rate": r.water_access_rate,
            "sanitation_rate": r.sanitation_rate,
            "electricity_rate": r.electricity_rate,
            "gas_rate": r.gas_rate,
            "source": r.source,
        }
        for r in records
    ]
