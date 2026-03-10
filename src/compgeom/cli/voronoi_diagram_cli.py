from __future__ import annotations

from compgeom.cli._shared import demo_points
from compgeom.mesh.voronoi_diagram import VoronoiDiagram


def main() -> int:
    points = demo_points()
    boundary_type = "square"
    diagram = VoronoiDiagram()
    print(f"Using {boundary_type} boundary.")
    diagram.compute(points, boundary_type=boundary_type)
    cells = diagram.cells
    print(f"Voronoi Diagram: {len(cells)} cells generated.")
    for point, cell in cells:
        print(f"\nPoint {point.id} at ({point.x}, {point.y}) Cell Vertices:")
        for vertex in cell:
            print(f"  ({vertex.x:.4f}, {vertex.y:.4f})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
