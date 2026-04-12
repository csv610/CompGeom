from __future__ import annotations

import argparse
from .._shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.mesh import VoronoiDiagram


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a Voronoi diagram for points."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument(
        "--boundary-type",
        default="square",
        help="Boundary type passed to the Voronoi diagram builder.",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Visualize the Voronoi diagram using pyvista.",
    )
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1

    boundary_type = args.boundary_type
    diagram = VoronoiDiagram()
    print(f"Using {boundary_type} boundary.")
    diagram.compute(points, boundary_type=boundary_type)
    cells = diagram.cells
    print(f"Voronoi Diagram: {len(cells)} cells generated.")

    all_cells = []
    for point, cell in cells:
        print(f"\nPoint {point.id} at ({point.x}, {point.y}) Cell Vertices:")
        for vertex in cell:
            print(f"  ({vertex.x:.4f}, {vertex.y:.4f})")
        if args.visualize:
            all_cells.append(cell)

    if args.visualize:
        visualize_with_pyvista(points=points, polygons=all_cells)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
