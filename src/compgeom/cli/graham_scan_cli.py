from __future__ import annotations

from compgeom import graham_scan
from compgeom.cli._shared import demo_points


def main() -> int:
    points = demo_points()
    hull = graham_scan(points)
    print(f"Convex Hull (Graham Scan) has {len(hull)} vertices:")
    for point in hull:
        print(f"  ({point.x:.4f}, {point.y:.4f})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
