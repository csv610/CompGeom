from __future__ import annotations

import argparse
from compgeom.kernel import Point2D
from compgeom.polygon.polygon_smoothing import (
    resample_polygon,
    mean_curvature_flow_polygon,
)
from compgeom.mesh import MeshImporter, MeshExporter, Mesh
from compgeom.polygon.polygon import Polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Smooth a polygon using Mean Curvature Flow."
    )
    parser.add_argument("input", help="Path to input file.")
    parser.add_argument(
        "--iterations", type=int, default=100, help="Number of smoothing iterations"
    )
    parser.add_argument(
        "--no_center",
        action="store_false",
        dest="fix_centroid",
        help="Do not fix centroid at (0,0)",
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output file for smoothed result"
    )

    args = parser.parse_args(argv)
    fix_centroid = getattr(args, "fix_centroid", True)

    print(f"Reading input from {args.input}...")
    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    print(f"Initial input: {len(mesh.vertices)} vertices.")

    print(f"Applying MCF for {args.iterations} iterations...")
    if fix_centroid:
        print("Constraint: Centroid is fixed at (0,0).")

    smoothed = mean_curvature_flow_polygon(
        mesh,
        args.iterations,
        keep_perimeter=True,
        fix_centroid=fix_centroid,
    )

    try:
        MeshExporter.write(args.output, smoothed)
        print(f"Smoothed result written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
