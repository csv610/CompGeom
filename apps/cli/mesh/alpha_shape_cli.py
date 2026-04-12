from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.mesh.surface.alpha_shapes import AlphaShape
from compgeom.kernel import Point2D, Point3D


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the alpha shape (concave hull) of a point set."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input file (OBJ, OFF, STL, PLY or text points)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output file."
    )
    parser.add_argument(
        "-a", "--alpha", type=float, required=True, help="Alpha parameter (radius of the rolling ball)."
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
    # Check if all points have zero z
    if is_3d:
        is_actually_3d = any(abs(getattr(p, "z", 0.0)) > 1e-9 for p in points)
        if not is_actually_3d:
            is_3d = False

    if is_3d:
        print(f"Computing 3D alpha shape with alpha={args.alpha}...")
        points_3d = [Point3D(p.x, p.y, getattr(p, "z", 0.0)) for p in points]
        try:
            result_mesh = AlphaShape.compute_3d(points_3d, args.alpha)
            MeshExporter.write(args.output, result_mesh)
            print(f"3D Alpha shape written to {args.output}")
        except Exception as e:
            print(f"Error computing 3D alpha shape: {e}")
            return 1
    else:
        print(f"Computing 2D alpha shape with alpha={args.alpha}...")
        points_2d = [Point2D(p.x, p.y) for p in points]
        try:
            edges = AlphaShape.compute_2d(points_2d, args.alpha)
            # Save edges as a mesh with only edges
            MeshExporter.write(args.output, points_2d, edges=edges)
            print(f"2D Alpha shape (edges) written to {args.output}")
        except Exception as e:
            print(f"Error computing 2D alpha shape: {e}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
