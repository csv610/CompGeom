from __future__ import annotations

import argparse
import sys
from .._shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.polygon.convex_hull import GrahamScan
from compgeom.mesh import meshio


def load_points_from_mesh(file_path: str) -> list | None:
    try:
        mesh = meshio.from_file(file_path)
        vertices = mesh.vertices
        if not vertices:
            print("Error: Mesh has no vertices.")
            return None
        from compgeom import Point2D

        is_3d = hasattr(vertices[0], "z")
        if is_3d:
            return [Point2D(v.x, v.y, i) for i, v in enumerate(vertices)]
        return vertices
    except Exception as e:
        print(f"Error reading mesh file: {e}")
        return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute the convex hull of a point set."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to input file (optional, reads from stdin if omitted).",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Visualize the convex hull using pyvista.",
    )
    args = parser.parse_args(argv)

    points = None

    if args.input:
        ext = args.input.lower()
        if ext.endswith((".obj", ".off", ".stl", ".ply")):
            points = load_points_from_mesh(args.input)
            if points is None:
                return 1
        else:
            lines = read_input_lines(args.input)
            if not lines:
                print("Error: No input points provided.")
                return 1
            points = parse_points(lines)
    else:
        if sys.stdin.isatty():
            print(
                "Error: No input points provided. Use a file, mesh file, or provide points via stdin."
            )
            return 1
        lines = read_input_lines(None)
        if not lines:
            print("Error: No input points provided.")
            return 1
        points = parse_points(lines)

    if not points:
        print("Error: Could not parse points from input.")
        return 1

    hull = GrahamScan().generate(points)
    print(f"Convex Hull (Graham Scan) has {len(hull)} vertices:")
    for point in hull:
        print(f"  ({point.x:.4f}, {point.y:.4f})")

    if args.visualize:
        visualize_with_pyvista(points=points, polygons=[hull])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
