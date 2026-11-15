from math import cos, radians
from fastapi import HTTPException

def geojson_area_hectares(geometry: dict | None) -> float:
    if not geometry: return 0.0
    if geometry.get("type") != "Polygon" or not isinstance(geometry.get("coordinates"), list) or not geometry["coordinates"]:
        raise HTTPException(422, "Boundary must be a GeoJSON Polygon")
    ring = geometry["coordinates"][0]
    if len(ring) < 4 or ring[0] != ring[-1]: raise HTTPException(422, "Polygon must be closed and contain at least three vertices")
    try:
        points = [(float(p[0]), float(p[1])) for p in ring]
    except (ValueError, TypeError, IndexError): raise HTTPException(422, "Invalid polygon coordinates")
    if any(not -180 <= x <= 180 or not -90 <= y <= 90 for x, y in points): raise HTTPException(422, "Polygon coordinates out of range")
    mean_lat = sum(y for _, y in points) / len(points)
    scale_x, scale_y = 111_320 * cos(radians(mean_lat)), 110_574
    area = abs(sum((points[i][0]*scale_x * points[i+1][1]*scale_y) - (points[i+1][0]*scale_x * points[i][1]*scale_y) for i in range(len(points)-1))) / 2
    return round(area / 10_000, 3)
