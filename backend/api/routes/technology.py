from typing import Optional
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_AsGeoJSON

from database import get_db
from models.technology import InternetPenetration, CoverageZone, RDSpending, DigitalLiteracy
from schemas.common import GeoJSONFeatureCollection

router = APIRouter()


@router.get("/internet-penetration")
async def internet_penetration(
    year: Optional[int] = None,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(InternetPenetration)
    if year:
        stmt = stmt.where(InternetPenetration.year == year)
    if department_id:
        stmt = stmt.where(InternetPenetration.department_id == department_id)
    result = await db.execute(stmt.order_by(InternetPenetration.year))
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "year": r.year,
            "department_id": r.department_id,
            "percentage": r.percentage,
            "fixed_broadband_per_100": r.fixed_broadband_per_100,
            "mobile_per_100": r.mobile_per_100,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/coverage", response_model=GeoJSONFeatureCollection)
async def coverage_geojson(
    technology: Optional[str] = Query(None, description="4G or 5G"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        CoverageZone.id,
        CoverageZone.operator,
        CoverageZone.technology,
        ST_AsGeoJSON(CoverageZone.geometry).label("geom"),
    ).where(CoverageZone.geometry.isnot(None))
    if technology:
        stmt = stmt.where(CoverageZone.technology == technology)
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {"id": r.id, "operator": r.operator, "technology": r.technology},
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/rd-spending")
async def rd_spending(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RDSpending).order_by(RDSpending.year))
    records = result.scalars().all()
    return [
        {
            "year": r.year,
            "percentage_of_gdp": r.percentage_of_gdp,
            "amount_usd": r.amount_usd,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/digital-literacy")
async def digital_literacy(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(DigitalLiteracy)
    if year:
        stmt = stmt.where(DigitalLiteracy.year == year)
    result = await db.execute(stmt.order_by(DigitalLiteracy.year))
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "year": r.year,
            "department_id": r.department_id,
            "rate": r.rate,
            "age_group": r.age_group,
            "source": r.source,
        }
        for r in records
    ]
