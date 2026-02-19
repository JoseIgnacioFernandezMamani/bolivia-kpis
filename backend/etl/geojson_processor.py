"""GeoJSON processing utilities using Shapely."""
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from shapely.geometry import shape, mapping
from shapely.ops import transform as shapely_transform
import shapely

logger = logging.getLogger(__name__)


def simplify_geometry(geometry_dict: Dict[str, Any], tolerance: float = 0.001) -> Dict[str, Any]:
    """Simplify a GeoJSON geometry dict using the Douglas-Peucker algorithm.

    Parameters
    ----------
    geometry_dict:
        A GeoJSON geometry object (``{"type": ..., "coordinates": ...}``).
    tolerance:
        Simplification tolerance in degrees (default 0.001 ≈ ~100 m at equator).

    Returns
    -------
    Simplified GeoJSON geometry dict.
    """
    geom = shape(geometry_dict)
    simplified = geom.simplify(tolerance, preserve_topology=True)
    return mapping(simplified)


def csv_to_geojson(
    rows: List[Dict[str, Any]],
    lat_field: str = "latitude",
    lon_field: str = "longitude",
    properties: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Convert a list of dicts (with lat/lon fields) to a GeoJSON FeatureCollection.

    Parameters
    ----------
    rows:
        List of row dicts from a CSV file.
    lat_field / lon_field:
        Column names for latitude and longitude.
    properties:
        Which fields to include as feature properties. If None, all fields except
        lat/lon are included.

    Returns
    -------
    GeoJSON FeatureCollection dict.
    """
    features = []
    for row in rows:
        try:
            lat = float(row[lat_field])
            lon = float(row[lon_field])
        except (KeyError, ValueError, TypeError):
            logger.warning("Skipping row with missing/invalid coordinates: %s", row)
            continue

        if properties is None:
            props = {k: v for k, v in row.items() if k not in (lat_field, lon_field)}
        else:
            props = {k: row.get(k) for k in properties}

        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
                "properties": props,
            }
        )

    return {"type": "FeatureCollection", "features": features}


def validate_geojson(geojson: Dict[str, Any]) -> bool:
    """Minimal structural validation of a GeoJSON object.

    Returns True if valid, False otherwise (and logs the issue).
    """
    if not isinstance(geojson, dict):
        logger.error("GeoJSON must be a dict, got %s", type(geojson))
        return False

    geo_type = geojson.get("type")
    if geo_type not in {"FeatureCollection", "Feature", "GeometryCollection",
                        "Point", "MultiPoint", "LineString", "MultiLineString",
                        "Polygon", "MultiPolygon"}:
        logger.error("Unknown GeoJSON type: %s", geo_type)
        return False

    if geo_type == "FeatureCollection" and not isinstance(geojson.get("features"), list):
        logger.error("FeatureCollection missing 'features' array")
        return False

    # Try parsing all geometries with Shapely
    if geo_type == "FeatureCollection":
        for feat in geojson["features"]:
            geom = feat.get("geometry")
            if geom:
                try:
                    shape(geom)
                except Exception as exc:
                    logger.warning("Invalid geometry in feature: %s", exc)
                    return False

    return True


def save_processed(geojson: Dict[str, Any], output_path: str) -> Path:
    """Serialise a GeoJSON dict to a file and return the Path.

    Creates parent directories if they do not exist.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(geojson, ensure_ascii=False, indent=2))
    logger.info("Saved processed GeoJSON to %s (%d features)", path, len(geojson.get("features", [])))
    return path
