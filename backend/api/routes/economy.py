from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2.functions import ST_AsGeoJSON
import json

from database import get_db
from models.economy import GDPPerCapita, Inflation, Export, PublicContract, Department
from schemas.common import PaginatedResponse, GeoJSONFeatureCollection

router = APIRouter()


@router.get("/gdp", response_model=PaginatedResponse)
async def list_gdp(
    department_id: Optional[int] = None,
    year: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(GDPPerCapita)
    if department_id:
        stmt = stmt.where(GDPPerCapita.department_id == department_id)
    if year:
        stmt = stmt.where(GDPPerCapita.year == year)

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "department_id": r.department_id,
                "year": r.year,
                "value_usd": r.value_usd,
                "source": r.source,
            }
            for r in items
        ],
    }


@router.get("/gdp/{department_id}")
async def get_gdp_by_department(department_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(GDPPerCapita).where(GDPPerCapita.department_id == department_id).order_by(GDPPerCapita.year)
    )
    records = result.scalars().all()
    return [{"year": r.year, "value_usd": r.value_usd, "source": r.source} for r in records]


@router.get("/inflation")
async def list_inflation(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Inflation).order_by(Inflation.year, Inflation.month)
    if year:
        stmt = stmt.where(Inflation.year == year)
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {"id": r.id, "year": r.year, "month": r.month, "rate": r.rate, "source": r.source}
        for r in records
    ]


@router.get("/exports")
async def list_exports(
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Export).order_by(Export.year)
    if year:
        stmt = stmt.where(Export.year == year)
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [
        {
            "id": r.id,
            "product": r.product,
            "year": r.year,
            "value_usd": r.value_usd,
            "percentage_of_total": r.percentage_of_total,
            "source": r.source,
        }
        for r in records
    ]


@router.get("/contracts")
async def list_contracts(
    department_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PublicContract)
    if department_id:
        stmt = stmt.where(PublicContract.department_id == department_id)

    total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "amount": r.amount,
                "contractor": r.contractor,
                "department_id": r.department_id,
                "date": str(r.date) if r.date else None,
                "sicoes_id": r.sicoes_id,
                "source": r.source,
            }
            for r in items
        ],
    }


@router.get("/contracts/geojson", response_model=GeoJSONFeatureCollection)
async def contracts_geojson(
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(
        PublicContract.id,
        PublicContract.title,
        PublicContract.amount,
        PublicContract.contractor,
        PublicContract.department_id,
        ST_AsGeoJSON(PublicContract.geometry).label("geom"),
    ).where(PublicContract.geometry.isnot(None))
    if department_id:
        stmt = stmt.where(PublicContract.department_id == department_id)

    rows = (await db.execute(stmt)).all()
    features = [
        {
            "type": "Feature",
            "geometry": json.loads(r.geom),
            "properties": {
                "id": r.id,
                "title": r.title,
                "amount": r.amount,
                "contractor": r.contractor,
                "department_id": r.department_id,
            },
        }
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}
