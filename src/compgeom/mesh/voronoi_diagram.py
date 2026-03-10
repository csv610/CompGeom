"""Triangulation and Voronoi algorithms."""

from __future__ import annotations

import math

from ..geo_math.geometry import (
    Point,
    clip_polygon,
    cross_product,
    sub,
)
from .delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    Triangle,
    build_topology,
    triangulate,
)


class VoronoiDiagram:
    """
    Computes and stores a Voronoi Diagram for a set of points within a boundary.
    """

    def __init__(self):
        self.points: list[Point] = []
        self.boundary: list[Point] = []
        self.cells: list[tuple[Point, list[Point]]] = []

    def compute(self, points: list[Point], boundary_type: str = "square") -> "PolygonMesh":
        """
        Computes the Voronoi cells using a clipping algorithm.
        The boundary is used to trim infinite rays from the Voronoi cells.
        Returns a PolygonMesh object.
        """
        from .mesh import PolygonMesh

        if not points:
            return PolygonMesh([], [])

        # 1. Determine bounding box and generate boundary
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)

        width = max_x - min_x
        height = max_y - min_y
        cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
        max_dim = max(width, height, 1.0)
        
        # User boundary: used for the final trim
        size = max_dim * 1.5
        if boundary_type == "circle":
            self.boundary = self.get_circle_boundary(radius=size / 2, center=(cx, cy))
        else:
            self.boundary = self.get_square_boundary(size=size, center=(cx, cy))

        # 2. Infinite box to represent "rays" during bisector clipping
        # This keeps the "algorithm" logic separate from the user boundary.
        inf_size = max_dim * 1e6
        inf_box = self.get_square_boundary(size=inf_size, center=(cx, cy))
        
        self.points = points
        self.cells = []
        unique_vertices = []
        vertex_to_idx = {}

        def get_v_idx(p: Point) -> int:
            key = (round(p.x, 8), round(p.y, 8))
            if key not in vertex_to_idx:
                vertex_to_idx[key] = len(unique_vertices)
                unique_vertices.append(p)
            return vertex_to_idx[key]

        face_indices = []
        for point in self.points:
            # Start with the infinite cell (simulating rays)
            cell = list(inf_box)
            
            # Clip by all perpendicular bisectors (The core algorithm)
            for other in self.points:
                if point == other:
                    continue
                midpoint = Point((point.x + other.x) / 2, (point.y + other.y) / 2)
                direction = sub(other, point)
                bisector_end = Point(midpoint.x - direction.y, midpoint.y + direction.x)
                
                # Keep the side containing the site 'point'
                if cross_product(midpoint, bisector_end, point) < 0:
                    cell = clip_polygon(cell, bisector_end, midpoint)
                else:
                    cell = clip_polygon(cell, midpoint, bisector_end)
            
            # Use the boundary to clip the resulting Voronoi rays
            for i in range(len(self.boundary)):
                p1, p2 = self.boundary[i], self.boundary[(i + 1) % len(self.boundary)]
                cell = clip_polygon(cell, p1, p2)
            
            self.cells.append((point, cell))
            if cell:
                face_indices.append(tuple(get_v_idx(p) for p in cell))
        
        return PolygonMesh(unique_vertices, face_indices)

    @staticmethod
    def get_square_boundary(size: float = 100, center: tuple[float, float] = (50, 50)) -> list[Point]:
        """Generates a square boundary polygon."""
        cx, cy = center
        half_size = size / 2
        return [
            Point(cx - half_size, cy - half_size),
            Point(cx + half_size, cy - half_size),
            Point(cx + half_size, cy + half_size),
            Point(cx - half_size, cy + half_size),
        ]

    @staticmethod
    def get_circle_boundary(radius: float = 50, center: tuple[float, float] = (50, 50), n_segments: int = 64) -> list[Point]:
        """Generates a circular boundary polygon."""
        cx, cy = center
        return [
            Point(cx + radius * math.cos(2 * math.pi * index / n_segments), 
                  cy + radius * math.sin(2 * math.pi * index / n_segments))
            for index in range(n_segments)
        ]


__all__ = [
    "DTriangle",
    "DelaunayMesher",
    "DynamicDelaunay",
    "MeshTriangle",
    "Triangle",
    "VoronoiDiagram",
    "build_topology",
    "triangulate",
]

if __name__ == "__main__":
    import argparse
    import random
    from ..graphics.geo_plot import GeomPlot
    from .mesh_io import MeshIO

    parser = argparse.ArgumentParser(description="Generate and plot a Voronoi Diagram.")
    parser.add_argument("-n", "--points", type=int, default=50, help="Number of random points (default: 50)")
    parser.add_argument("-b", "--boundary", choices=["square", "circle"], default="square", help="Boundary type (default: square)")
    parser.add_argument("-o", "--output", type=str, nargs="+", default=["voronoi.png"], help="Output file names (e.g., voronoi.png voronoi.off)")

    args = parser.parse_args()

    # Generate random points in a 1000x1000 area
    points = [Point(random.uniform(0, 1000), random.uniform(0, 1000), id=i) for i in range(args.points)]

    vd = VoronoiDiagram()
    mesh = vd.compute(points, boundary_type=args.boundary)

    for out_file in args.output:
        ext = out_file.rsplit(".", 1)[-1].lower()
        if ext in ["png", "svg"]:
            img_data = GeomPlot.get_image(vd, format=ext)
            mode = "wb" if ext == "png" else "w"
            with open(out_file, mode) as f:
                f.write(img_data)
            print(f"Saved image to {out_file}")
        elif f".{ext}" in MeshIO._handlers:
            MeshIO.write(out_file, mesh.vertices, mesh.elements)
            print(f"Saved mesh to {out_file}")
        else:
            print(f"Unsupported format: {ext}")
