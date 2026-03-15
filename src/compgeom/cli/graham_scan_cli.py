from __future__ import annotations

import argparse

from compgeom.cli._shared import demo_points, visualize_with_pyvista
from compgeom.polygon.convex_hull import GrahamScan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the convex hull of a demo point set.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in point set.")
    parser.add_argument("--visualize", action="store_true", help="Visualize the convex hull using pyvista.")
    args = parser.parse_args(argv)
    points = demo_points()
    hull = GrahamScan().generate(points)
    print(f"Convex Hull (Graham Scan) has {len(hull)} vertices:")
    for point in hull:
        print(f"  ({point.x:.4f}, {point.y:.4f})")
        
    if args.visualize:
        visualize_with_pyvista(points=points, polygons=[hull])
        
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
