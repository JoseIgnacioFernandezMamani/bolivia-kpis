from typing import Optional
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2.functions import ST_AsGeoJSON

from database import get_db
from models.politics import ElectionResult, SocialConflict, TIOCTerritory, DemocracyIndex, CorruptionIndex
from schemas.common import PaginatedResponse, GeoJSONFeatureCollection

router = APIRouter()


@router.get("/elections", response_model=PaginatedResponse)
async def list_elections(
    year: Optional[int] = None,
    department_id: Optional[int] = None,
    election_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ElectionResult)
    if year:
        stmt = stmt.where(ElectionResult.year == year)
    if department_id:
        stmt = stmt.where(ElectionResult.department_id == department_id)
    if election_type:
        stmt = stmt.where(ElectionResult.election_type == election_type)

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "year": r.year,
                "election_type": r.election_type,
                "department_id": r.department_id,
                "party": r.party,
                "candidate": r.candidate,
                "votes": r.votes,
                "percentage": r.percentage,
            }
            for r in items
        ],
    }


@router.get("/elections/geojson", response_model=GeoJSONFeatureCollection)
async def elections_geojson(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        ElectionResult.id,
        ElectionResult.year,
        ElectionResult.party,
        ElectionResult.candidate,
        ElectionResult.votes,
        ElectionResult.percentage,
        ST_AsGeoJSON(ElectionResult.geometry).label("geom"),
    ).where(ElectionResult.geometry.isnot(None))
    if year:
        stmt = stmt.where(ElectionResult.year == year)

    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "year": r.year,
                "party": r.party,
                "candidate": r.candidate,
                "votes": r.votes,
                "percentage": r.percentage,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/conflicts")
async def list_conflicts(
    department_id: Optional[int] = None,
    conflict_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SocialConflict)
    if department_id:
        stmt = stmt.where(SocialConflict.department_id == department_id)
    if conflict_type:
        stmt = stmt.where(SocialConflict.type == conflict_type)
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "department_id": r.department_id,
            "type": r.type,
            "start_date": str(r.start_date) if r.start_date else None,
            "end_date": str(r.end_date) if r.end_date else None,
            "description": r.description,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/conflicts/geojson", response_model=GeoJSONFeatureCollection)
async def conflicts_geojson(db: AsyncSession = Depends(get_db)):
    stmt = select(
        SocialConflict.id,
        SocialConflict.title,
        SocialConflict.type,
        ST_AsGeoJSON(SocialConflict.geometry).label("geom"),
    ).where(SocialConflict.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {"id": r.id, "title": r.title, "type": r.type},
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/tioc", response_model=GeoJSONFeatureCollection)
async def tioc_geojson(db: AsyncSession = Depends(get_db)):
    stmt = select(
        TIOCTerritory.id,
        TIOCTerritory.name,
        TIOCTerritory.ethnicity,
        TIOCTerritory.area_ha,
        ST_AsGeoJSON(TIOCTerritory.geometry).label("geom"),
    ).where(TIOCTerritory.geometry.isnot(None))
    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "name": r.name,
                "ethnicity": r.ethnicity,
                "area_ha": r.area_ha,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}


@router.get("/democracy-index")
async def democracy_index(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DemocracyIndex).order_by(DemocracyIndex.year))
    records = result.scalars().all()
    return [{"year": r.year, "score": r.score, "category": r.category, "source": r.source} for r in records]


@router.get("/corruption-index")
async def corruption_index(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CorruptionIndex).order_by(CorruptionIndex.year))
    records = result.scalars().all()
    return [{"year": r.year, "cpi_score": r.cpi_score, "rank": r.rank, "source": r.source} for r in records]
