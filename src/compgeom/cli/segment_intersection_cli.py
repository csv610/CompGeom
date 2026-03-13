from __future__ import annotations

import argparse

from compgeom import Point2D
from compgeom import do_intersect
from compgeom.cli._shared import demo_points


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test intersection between two demo segments.")
    parser.parse_args(argv)
    points = demo_points()
    p1, q1 = points[0], points[4]
    p2, q2 = Point2D(-0.5, 2.5), Point2D(4.0, 0.5)
    intersect = do_intersect(p1, q1, p2, q2)
    print(f"Segment 1: ({p1.x}, {p1.y}) to ({q1.x}, {q1.y})\nSegment 2: ({p2.x}, {p2.y}) to ({q2.x}, {q2.y})\nResult: Intersect? {intersect}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
