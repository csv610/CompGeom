from __future__ import annotations

from compgeom import get_polygon_properties
from compgeom.cli._shared import demo_polygon


def main() -> int:
    points = demo_polygon()
    area, centroid, orientation = get_polygon_properties(points)
    print(f"Polygon Properties:\n  Area:        {area:.4f}\n  Centroid:    ({centroid.x:.4f}, {centroid.y:.4f})\n  Orientation: {orientation}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
