from __future__ import annotations

import argparse
from ._shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.mesh import triangulate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a triangle mesh from points."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument(
        "--visualize", action="store_true", help="Visualize the mesh using pyvista."
    )
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1

    triangles, skipped = triangulate(points)
    if skipped:
        print("Skipped Points:")
        for point, reason in skipped:
            print(f"  {point}: {reason}")
    print(f"\nFinal Mesh: {len(triangles)} active triangles constructed.")

    faces = []
    # Map points to indices for pyvista
    point_to_idx = {p: i for i, p in enumerate(points)}

    for index, (a, b, c) in enumerate(triangles):
        ids = sorted([a.id, b.id, c.id])
        print(f"Triangle {index:3}: {ids[0]:3}, {ids[1]:3}, {ids[2]:3}")
        if args.visualize:
            faces.append([point_to_idx[a], point_to_idx[b], point_to_idx[c]])

    if args.visualize:
        visualize_with_pyvista(points=points, faces=faces)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
