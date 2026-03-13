from __future__ import annotations

import argparse

from compgeom import minkowski_sum
from compgeom.cli._shared import demo_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the Minkowski sum of two demo polygons.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in polygons.")
    args = parser.parse_args(argv)
    polygon_a = demo_polygon()[:4]
    polygon_b = [point.__class__(point.x * 0.5, point.y * 0.5) for point in demo_polygon()[2:6]]
    result = minkowski_sum(polygon_a, polygon_b)
    print(f"Minkowski Sum result ({len(result)} vertices):")
    for point in result:
        print(f"  ({point.x:.4f}, {point.y:.4f})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
