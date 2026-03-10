from __future__ import annotations

from compgeom import Point
from compgeom import is_point_in_polygon
from compgeom.cli._shared import demo_polygon


def main() -> int:
    target = Point(2.0, 2.0)
    polygon = demo_polygon()
    is_in = is_point_in_polygon(target, polygon)
    print(f"Point {target} is {'INSIDE' if is_in else 'OUTSIDE'} the polygon.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
