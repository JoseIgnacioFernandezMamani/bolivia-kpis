from typing import Optional
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_AsGeoJSON

from database import get_db
from models.environment import (
    DeforestationZone,
    ProtectedArea,
    MiningConcession,
    LithiumSaltFlat,
    CO2Emission,
    ForestFire,
)
from schemas.common import GeoJSONFeatureCollection

router = APIRouter()


@router.get("/deforestation", response_model=GeoJSONFeatureCollection)
async def deforestation_geojson(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        DeforestationZone.id,
        DeforestationZone.year,
        DeforestationZone.area_ha,
        DeforestationZone.department_id,
        ST_AsGeoJSON(DeforestationZone.geometry).label("geom"),
    ).where(DeforestationZone.geometry.isnot(None))
    if year:
        stmt = stmt.where(DeforestationZone.year == year)
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "year": r.year,
                "area_ha": r.area_ha,
                "department_id": r.department_id,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/protected-areas", response_model=GeoJSONFeatureCollection)
async def protected_areas_geojson(db: AsyncSession = Depends(get_db)):
    stmt = select(
        ProtectedArea.id,
        ProtectedArea.name,
        ProtectedArea.category,
        ProtectedArea.area_ha,
        ST_AsGeoJSON(ProtectedArea.geometry).label("geom"),
    ).where(ProtectedArea.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "area_ha": r.area_ha,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/mining", response_model=GeoJSONFeatureCollection)
async def mining_geojson(db: AsyncSession = Depends(get_db)):
    stmt = select(
        MiningConcession.id,
        MiningConcession.name,
        MiningConcession.mineral,
        MiningConcession.company,
        MiningConcession.area_ha,
        ST_AsGeoJSON(MiningConcession.geometry).label("geom"),
    ).where(MiningConcession.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "mineral": r.mineral,
                "company": r.company,
                "area_ha": r.area_ha,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/lithium", response_model=GeoJSONFeatureCollection)
async def lithium_geojson(db: AsyncSession = Depends(get_db)):
    stmt = select(
        LithiumSaltFlat.id,
        LithiumSaltFlat.name,
        LithiumSaltFlat.estimated_reserves_mt,
        ST_AsGeoJSON(LithiumSaltFlat.geometry).label("geom"),
    ).where(LithiumSaltFlat.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "estimated_reserves_mt": r.estimated_reserves_mt,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/co2")
async def co2_emissions(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CO2Emission)
    if year:
        stmt = stmt.where(CO2Emission.year == year)
    result = await db.execute(stmt.order_by(CO2Emission.year))
    records = result.scalars().all()
    return [
        {"year": r.year, "sector": r.sector, "value_mt": r.value_mt, "source": r.source}
        for r in records
    ]


@router.get("/fires", response_model=GeoJSONFeatureCollection)
async def forest_fires_geojson(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        ForestFire.id,
        ForestFire.detected_date,
        ForestFire.confidence,
        ForestFire.frp,
        ForestFire.satellite,
        ST_AsGeoJSON(ForestFire.geometry).label("geom"),
    ).where(ForestFire.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "detected_date": str(r.detected_date),
                "confidence": r.confidence,
                "frp": r.frp,
                "satellite": r.satellite,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}
