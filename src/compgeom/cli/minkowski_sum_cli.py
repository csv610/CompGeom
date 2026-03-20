from __future__ import annotations

import argparse

from compgeom.cli._shared import demo_polygon, visualize_with_pyvista
from compgeom.mesh.polygon.minkowski import MinkowskiSum


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the Minkowski sum of two demo polygons.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in polygons.")
    parser.add_argument("--visualize", action="store_true", help="Visualize the Minkowski sum using pyvista.")
    args = parser.parse_args(argv)
    polygon_a = demo_polygon()[:4]
    polygon_b = [point.__class__(point.x * 0.5, point.y * 0.5) for point in demo_polygon()[2:6]]
    
    # Using MinkowskiSum class directly if minkowski_sum is not available in namespace
    result = MinkowskiSum.compute(polygon_a, polygon_b)
    
    print(f"Minkowski Sum result ({len(result)} vertices):")
    for point in result:
        print(f"  ({point.x:.4f}, {point.y:.4f})")
        
    if args.visualize:
        visualize_with_pyvista(polygons=[polygon_a, polygon_b, result])
        
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
