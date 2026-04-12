from __future__ import annotations

import argparse
from compgeom import Point2D
from .._shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.polygon.polygon_metrics import is_point_in_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test whether a point lies inside a polygon.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--point", nargs=2, type=float, help="Query point as x y")
    parser.add_argument("--visualize", action="store_true", help="Visualize the point-in-polygon test using pyvista.")
    args = parser.parse_args(argv)
    
    if not args.point:
        print("Error: No query point provided. Use --point x y")
        return 1
        
    target = Point2D(args.point[0], args.point[1])
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No polygon provided.")
        return 1
    polygon = parse_points(lines)
    if not polygon:
        print("Error: Could not parse polygon from input.")
        return 1
        
    is_in = is_point_in_polygon(target, polygon)
    print(f"Point {target} is {'INSIDE' if is_in else 'OUTSIDE'} the polygon.")
    
    if args.visualize:
        visualize_with_pyvista(points=[target], polygons=[polygon])
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
