from typing import Optional
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_AsGeoJSON

from database import get_db
from models.security import CrimeRate, DrugSeizure, RoadSegment, Prison, HealthcareFacility
from schemas.common import GeoJSONFeatureCollection

router = APIRouter()


@router.get("/crime")
async def crime_rates(
    year: Optional[int] = None,
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CrimeRate)
    if year:
        stmt = stmt.where(CrimeRate.year == year)
    if department_id:
        stmt = stmt.where(CrimeRate.department_id == department_id)
    result = await db.execute(stmt.order_by(CrimeRate.year))
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "year": r.year,
            "department_id": r.department_id,
            "crime_type": r.crime_type,
            "count": r.count,
            "rate_per_100k": r.rate_per_100k,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/drug-seizures", response_model=GeoJSONFeatureCollection)
async def drug_seizures_geojson(
    drug_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        DrugSeizure.id,
        DrugSeizure.date,
        DrugSeizure.drug_type,
        DrugSeizure.quantity_kg,
        DrugSeizure.department_id,
        ST_AsGeoJSON(DrugSeizure.geometry).label("geom"),
    ).where(DrugSeizure.geometry.isnot(None))
    if drug_type:
        stmt = stmt.where(DrugSeizure.drug_type == drug_type)
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "date": str(r.date) if r.date else None,
                "drug_type": r.drug_type,
                "quantity_kg": r.quantity_kg,
                "department_id": r.department_id,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/roads", response_model=GeoJSONFeatureCollection)
async def roads_geojson(
    road_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        RoadSegment.id,
        RoadSegment.name,
        RoadSegment.road_type,
        RoadSegment.condition,
        RoadSegment.length_km,
        ST_AsGeoJSON(RoadSegment.geometry).label("geom"),
    ).where(RoadSegment.geometry.isnot(None))
    if road_type:
        stmt = stmt.where(RoadSegment.road_type == road_type)
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "road_type": r.road_type,
                "condition": r.condition,
                "length_km": r.length_km,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/prisons", response_model=GeoJSONFeatureCollection)
async def prisons_geojson(db: AsyncSession = Depends(get_db)):
    stmt = select(
        Prison.id,
        Prison.name,
        Prison.department_id,
        Prison.capacity,
        Prison.population,
        ST_AsGeoJSON(Prison.geometry).label("geom"),
    ).where(Prison.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "department_id": r.department_id,
                "capacity": r.capacity,
                "population": r.population,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/healthcare", response_model=GeoJSONFeatureCollection)
async def healthcare_geojson(
    facility_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        HealthcareFacility.id,
        HealthcareFacility.name,
        HealthcareFacility.facility_type,
        HealthcareFacility.department_id,
        HealthcareFacility.beds,
        ST_AsGeoJSON(HealthcareFacility.geometry).label("geom"),
    ).where(HealthcareFacility.geometry.isnot(None))
    if facility_type:
        stmt = stmt.where(HealthcareFacility.facility_type == facility_type)
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "facility_type": r.facility_type,
                "department_id": r.department_id,
                "beds": r.beds,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}
