from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.polygon.convex_hull import ConvexHull
from compgeom.kernel import Point2D, Point3D


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the convex hull of a point set in 2D or 3D."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input file (OBJ, OFF, STL, PLY or text points)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output file."
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=["scipy", "graham_scan", "monotone_chain", "quickhull", "chan"],
        default="scipy",
        help="Algorithm to use for 2D points (default: scipy).",
    )

    args = parser.parse_args(argv)

    try:
        # Try reading as mesh first
        try:
            mesh = MeshImporter.read(args.input)
            points = mesh.vertices
        except:
            # Fallback to parsing text points
            from .._shared import read_input_lines, parse_points
            lines = read_input_lines(args.input)
            points = parse_points(lines)
    except Exception as e:
        print(f"Error reading input points: {e}")
        return 1

    if not points:
        print("Error: No points found in input.")
        return 1

    is_3d = hasattr(points[0], "z") and abs(getattr(points[0], "z", 0.0)) > 1e-9
    if is_3d:
        # Extra check
        is_actually_3d = any(abs(getattr(p, "z", 0.0)) > 1e-9 for p in points)
        if not is_actually_3d:
            is_3d = False

    if is_3d:
        print("Computing 3D convex hull...")
        points_3d = [Point3D(p.x, p.y, getattr(p, "z", 0.0)) for p in points]
        try:
            hull_mesh = ConvexHull.generate(points_3d)
            MeshExporter.write(args.output, hull_mesh)
            print(f"3D Convex hull written to {args.output}")
        except Exception as e:
            print(f"Error computing 3D convex hull: {e}")
            return 1
    else:
        print(f"Computing 2D convex hull using {args.algorithm}...")
        points_2d = [Point2D(p.x, p.y) for p in points]
        try:
            hull_poly = ConvexHull.generate(points_2d, algorithm=args.algorithm)
            # hull_poly is a list of points
            # Save as a single face mesh
            from compgeom.polygon.polygon import Polygon
            poly = Polygon(hull_poly)
            MeshExporter.write(args.output, poly)
            print(f"2D Convex hull written to {args.output}")
        except Exception as e:
            print(f"Error computing 2D convex hull: {e}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
