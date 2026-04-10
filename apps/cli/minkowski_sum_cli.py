from __future__ import annotations

import argparse

from ._shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.mesh.polygon.minkowski import MinkowskiSum


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the Minkowski sum of two polygons.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--visualize", action="store_true", help="Visualize the Minkowski sum using pyvista.")
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input provided. Provide two polygons separated by 'NEXT'.")
        return 1
        
    poly_lines_a = []
    poly_lines_b = []
    current = poly_lines_a
    for line in lines:
        if line.strip().upper() == "NEXT":
            current = poly_lines_b
            continue
        current.append(line)
        
    if not poly_lines_b:
        print("Error: Provide two polygons separated by 'NEXT' line.")
        return 1

    polygon_a = parse_points(poly_lines_a)
    polygon_b = parse_points(poly_lines_b)
    
    if len(polygon_a) < 3 or len(polygon_b) < 3:
        print("Error: Both polygons must have at least 3 vertices.")
        return 1
    
    result = MinkowskiSum.compute(polygon_a, polygon_b)
    
    print(f"Minkowski Sum result ({len(result)} vertices):")
    for point in result:
        print(f"  ({point.x:.4f}, {point.y:.4f})")
        
    if args.visualize:
        visualize_with_pyvista(polygons=[polygon_a, polygon_b, result])
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
