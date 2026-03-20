"""Triangulation and Voronoi algorithms."""

from __future__ import annotations

import math
from typing import Iterable, Union

from compgeom.kernel import (
    Point2D,
    clip_polygon,
    cross_product,
    sub,
    triangle_circumcenter,
)
from compgeom.mesh.surface.trimesh.delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    Triangle,
    build_topology,
    triangulate,
)
from compgeom.mesh.surface.trimesh.delaunay_mesh_incremental import IncrementalDelaunayMesher, IncrementalTriangle


class VoronoiDiagram:
    """
    Computes and stores a Voronoi Diagram for a set of points within a boundary.
    Exploits duality with Delaunay Triangulation for O(N log N) performance.
    """

    def __init__(self):
        self.points: list[Point2D] = []
        self.boundary: list[Point2D] = []
        self.cells: list[tuple[Point2D, list[Point2D]]] = []

    def compute(self, points: list[Point2D], boundary_type: str = "square") -> "PolygonMesh":
        """
        Computes the Voronoi cells using the Delaunay Dual property.
        Returns a PolygonMesh object.
        """
        from compgeom.mesh.surface.polygon.polygon import PolygonMesh

        if not points:
            return PolygonMesh([], [])

        self.points = points
        
        # 1. Determine bounding box and generate boundary
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)

        width = max_x - min_x
        height = max_y - min_y
        cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
        max_dim = max(width, height, 1.0)
        
        size = max_dim * 1.5
        if boundary_type == "circle":
            self.boundary = self.get_circle_boundary(radius=size / 2, center=(cx, cy))
        else:
            self.boundary = self.get_square_boundary(size=size, center=(cx, cy))

        # 2. Compute Delaunay Triangulation (Stateful)
        mesher = IncrementalDelaunayMesher()
        mesher.triangulate(points)
        
        # 3. Precompute circumcenters for all active triangles
        tri_to_cc: dict[IncrementalTriangle, Point2D] = {}
        for tri in mesher.active_triangles:
            cc = triangle_circumcenter(*tri.vertices)
            if cc is None: # Collinear fallback
                v = tri.vertices
                cc = Point2D((v[0].x + v[1].x + v[2].x) / 3, (v[0].y + v[1].y + v[2].y) / 3)
            tri_to_cc[tri] = cc

        self.cells = []
        unique_vertices = []
        vertex_to_idx = {}

        def get_v_idx(p: Point2D) -> int:
            key = (round(p.x, 8), round(p.y, 8))
            if key not in vertex_to_idx:
                vertex_to_idx[key] = len(unique_vertices)
                unique_vertices.append(p)
            return vertex_to_idx[key]

        face_indices = []
        
        # 4. For each point, find the star of triangles and their circumcenters
        for site in self.points:
            star = mesher.vertex_to_triangles.get(site)
            if not star:
                continue
            
            sorted_star = self._sort_star(site, star)
            cell = [tri_to_cc[tri] for tri in sorted_star]
            
            # Clip by the boundary
            for i in range(len(self.boundary)):
                p1, p2 = self.boundary[i], self.boundary[(i + 1) % len(self.boundary)]
                cell = clip_polygon(cell, p1, p2)
            
            self.cells.append((site, cell))
            if cell:
                face_indices.append(tuple(get_v_idx(p) for p in cell))
        
        return PolygonMesh(unique_vertices, face_indices)

    def verify(self) -> bool:
        """
        Verifies the correctness of the Voronoi Diagram.
        Checks:
        1. Each site is inside its cell.
        2. Each cell is convex.
        3. Vertices of the cell are closer to their defining site than to others.
        """
        from compgeom.mesh.kernel import orientation_sign, length_sq, sub
        
        if not self.cells:
            return True

        for site, cell in self.cells:
            if not cell: continue
            
            n = len(cell)
            # 1. Site containment & 2. Convexity
            # We assume CCW orientation for the cell.
            for i in range(n):
                p1, p2 = cell[i], cell[(i + 1) % n]
                # Site containment: site should be on the left of each edge
                if orientation_sign(p1, p2, site) < 0:
                    print(f"Verification Failed: Site {site} is outside its cell edge ({p1}, {p2}).")
                    return False
                
                # Convexity: each vertex turn should be CCW
                p3 = cell[(i + 2) % n]
                if orientation_sign(p1, p2, p3) < 0:
                    print(f"Verification Failed: Cell for site {site} is not convex at ({p1}, {p2}, {p3}).")
                    return False

            # 3. Voronoi Property (Nearest Neighbor)
            for v in cell:
                d_site = length_sq(sub(v, site))
                for other_site in self.points:
                    if other_site == site: continue
                    d_other = length_sq(sub(v, other_site))
                    if d_other < d_site - 1e-7:
                        # Check if vertex is on boundary (clipping can move vertices)
                        on_boundary = any(abs(orientation_sign(self.boundary[j], self.boundary[(j+1)%len(self.boundary)], v)) == 0
                                         for j in range(len(self.boundary)))
                        if not on_boundary:
                            print(f"Verification Failed: Vertex {v} of site {site} is closer to {other_site}.")
                            return False
                            
        return True

    def _sort_star(self, site: Point2D, star: Iterable[IncrementalTriangle]) -> list[IncrementalTriangle]:
        """Sorts triangles around a site in CCW order using adjacency."""
        star_list = list(star)
        if not star_list: return []
        
        curr = star_list[0]
        sorted_tris = [curr]
        visited = {curr}
        
        # Walk CCW around the site
        temp = curr
        while True:
            idx = -1
            for i, v in enumerate(temp.vertices):
                if v == site:
                    idx = i; break
            if idx == -1: break
            
            next_tri = temp.neighbors[(idx + 1) % 3]
            if next_tri and next_tri in star and next_tri not in visited:
                sorted_tris.append(next_tri)
                visited.add(next_tri)
                temp = next_tri
            else:
                break
                
        # Walk CW around the site
        temp = curr
        while True:
            idx = -1
            for i, v in enumerate(temp.vertices):
                if v == site:
                    idx = i; break
            if idx == -1: break
            
            next_tri = temp.neighbors[(idx + 2) % 3]
            if next_tri and next_tri in star and next_tri not in visited:
                sorted_tris.insert(0, next_tri)
                visited.add(next_tri)
                temp = next_tri
            else:
                break
                
        return sorted_tris

    def plot(self, width: int = 1000, height: int = 1000, padding: int = 50) -> str:
        """Generates a standalone SVG for the Voronoi Diagram."""
        if not self.cells:
            return f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="white" /><text x="50" y="50">No Cells</text></svg>'

        # Get bounds
        all_pts = []
        for _, cell in self.cells: all_pts.extend(cell)
        all_pts.extend(self.points)
        
        min_x = min(p.x for p in all_pts)
        max_x = max(p.x for p in all_pts)
        min_y = min(p.y for p in all_pts)
        max_y = max(p.y for p in all_pts)
        
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0
        scale = min((width - 2*padding) / data_w, (height - 2*padding) / data_h)
        off_x = padding - min_x * scale + (width - 2*padding - data_w * scale) / 2
        off_y = padding - min_y * scale + (height - 2*padding - data_h * scale) / 2

        def to_c(p: Point2D):
            return off_x + p.x * scale, height - (off_y + p.y * scale)

        svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="white" />')
        
        # Draw cells
        for _, cell in self.cells:
            if not cell: continue
            pts = [to_c(p) for p in cell]
            pts_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
            svg.append(f'<polygon points="{pts_str}" fill="none" stroke="blue" stroke-width="0.5" />')
            
        # Draw sites
        site_r = 1.0 if len(self.points) > 1000 else 2.0
        for p in self.points:
            cx, cy = to_c(p)
            svg.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{site_r}" fill="red" />')
            
        svg.append('</svg>')
        return "\n".join(svg)

    @staticmethod
    def get_square_boundary(size: float = 100, center: tuple[float, float] = (50, 50)) -> list[Point2D]:
        """Generates a square boundary polygon."""
        cx, cy = center
        half_size = size / 2
        return [
            Point2D(cx - half_size, cy - half_size),
            Point2D(cx + half_size, cy - half_size),
            Point2D(cx + half_size, cy + half_size),
            Point2D(cx - half_size, cy + half_size),
        ]

    @staticmethod
    def get_circle_boundary(radius: float = 50, center: tuple[float, float] = (50, 50), n_segments: int = 64) -> list[Point2D]:
        """Generates a circular boundary polygon."""
        cx, cy = center
        return [
            Point2D(cx + radius * math.cos(2 * math.pi * index / n_segments), 
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
    import time
    from compgeom.graphics.geo_plot import GeomPlot
    from compgeom.mesh.meshio import MeshExporter

    parser = argparse.ArgumentParser(description="Generate and plot a Voronoi Diagram.")
    parser.add_argument("-n", "--points", type=int, default=50, help="Number of random points (default: 50)")
    parser.add_argument("-b", "--boundary", choices=["square", "circle"], default="square", help="Boundary type (default: square)")
    parser.add_argument("-o", "--output", type=str, nargs="+", default=["voronoi.png"], help="Output file names (e.g., voronoi.png voronoi.off)")

    args = parser.parse_args()

    # Generate random points in a 1000x1000 area
    points = [Point2D(random.uniform(0, 1000), random.uniform(0, 1000), id=i) for i in range(args.points)]

    start = time.time()
    vd = VoronoiDiagram()
    mesh = vd.compute(points, boundary_type=args.boundary)
    end = time.time()
    print(f"Computed Voronoi for {args.points} points in {end - start:.4f} seconds.")
    
    is_valid = vd.verify()
    print(f"Voronoi Verification: {'PASSED' if is_valid else 'FAILED'}")

    for out_file in args.output:
        ext = out_file.rsplit(".", 1)[-1].lower()
        if ext == "svg":
            with open(out_file, "w") as f:
                f.write(vd.plot())
            print(f"Saved SVG to {out_file}")
        elif ext == "png":
            try:
                img_data = GeomPlot.get_image(vd, format=ext)
                with open(out_file, "wb") as f:
                    f.write(img_data)
                print(f"Saved PNG to {out_file}")
            except Exception as e:
                print(f"Could not save PNG: {e}")
        elif f".{ext}" in MeshExporter._handlers:
            mesh.to_file(out_file)
            print(f"Saved mesh to {out_file}")
        else:
            print(f"Unsupported format: {ext}")
