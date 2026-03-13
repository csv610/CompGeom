from __future__ import annotations

import argparse

from compgeom import get_polygon_properties
from compgeom.cli._shared import demo_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute properties of a demo polygon.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in polygon.")
    args = parser.parse_args(argv)
    points = demo_polygon()
    area, centroid, orientation = get_polygon_properties(points)
    print(f"Polygon Properties:\n  Area:        {area:.4f}\n  Centroid:    ({centroid.x:.4f}, {centroid.y:.4f})\n  Orientation: {orientation}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
