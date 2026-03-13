from __future__ import annotations

import argparse

from compgeom import Point2D
from compgeom import is_point_in_polygon
from compgeom.cli._shared import demo_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test whether a demo point lies inside a demo polygon.")
    parser.add_argument("--demo", action="store_true", help="Run the built-in query.")
    args = parser.parse_args(argv)
    target = Point2D(2.0, 2.0)
    polygon = demo_polygon()
    is_in = is_point_in_polygon(target, polygon)
    print(f"Point {target} is {'INSIDE' if is_in else 'OUTSIDE'} the polygon.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
