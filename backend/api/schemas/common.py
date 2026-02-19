from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ExportFormat(str, Enum):
    json = "json"
    csv = "csv"
    geojson = "geojson"


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Any]


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Optional[GeoJSONGeometry]
    properties: Optional[Dict[str, Any]]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]
