"""Shared utilities for Delaunay tetrahedralization algorithms."""

from __future__ import annotations
import math
from typing import Iterable, TYPE_CHECKING, Tuple

from ....kernel import Point3D, hilbert_key


class PointGrid3D:
    """Simple 3D grid for fast nearest-neighbor search."""
    def __init__(self, points: Iterable[Point3D]):
        pts = list(points)
        if not pts:
            self.min_x = self.max_x = self.min_y = self.max_y = self.min_z = self.max_z = 0.0
            self.grid = {}
            self.cell_size = 1.0
            self.num_cells = 1
            return

        self.min_x = min(p.x for p in pts)
        self.max_x = max(p.x for p in pts)
        self.min_y = min(p.y for p in pts)
        self.max_y = max(p.y for p in pts)
        self.min_z = min(p.z for p in pts)
        self.max_z = max(p.z for p in pts)
        
        n = len(pts)
        self.num_cells = int(math.pow(n, 1/3)) + 1
        self.cell_size = max((self.max_x - self.min_x) / self.num_cells, 
                             (self.max_y - self.min_y) / self.num_cells,
                             (self.max_z - self.min_z) / self.num_cells,
                             0.1)
        
        self.grid: dict[tuple[int, int, int], list[Point3D]] = {}

    def _get_cell(self, p: Point3D) -> tuple[int, int, int]:
        return (int((p.x - self.min_x) / self.cell_size), 
                int((p.y - self.min_y) / self.cell_size),
                int((p.z - self.min_z) / self.cell_size))

    def add(self, p: Point3D):
        cell = self._get_cell(p)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(p)

    def find_nearest(self, p: Point3D) -> Point3D | None:
        if not self.grid:
            return None
            
        cx, cy, cz = self._get_cell(p)
        nearest = None
        min_dist_sq = float("inf")
        
        radius = 0
        while not nearest and radius < self.num_cells:
            for i in range(cx - radius, cx + radius + 1):
                for j in range(cy - radius, cy + radius + 1):
                    for k in range(cz - radius, cz + radius + 1):
                        if abs(i - cx) != radius and abs(j - cy) != radius and abs(k - cz) != radius:
                            continue
                        cell_points = self.grid.get((i, j, k))
                        if cell_points:
                            for cp in cell_points:
                                dist_sq = (p.x - cp.x)**2 + (p.y - cp.y)**2 + (p.z - cp.z)**2
                                if dist_sq < min_dist_sq:
                                    min_dist_sq = dist_sq
                                    nearest = cp
            radius += 1
        return nearest


def create_super_tetrahedron(points: Iterable[Point3D], scale: float = 100.0) -> tuple[Point3D, Point3D, Point3D, Point3D]:
    pts = list(points)
    if not pts:
        return (Point3D(0, 0, 100, id=-1), Point3D(100, 0, -100, id=-2), Point3D(-100, 100, -100, id=-3), Point3D(-100, -100, -100, id=-4))
        
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)
    
    dx = max_x - min_x
    dy = max_y - min_y
    dz = max_z - min_z
    delta = max(dx, dy, dz, 1.0) * scale
    
    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2
    
    # A large tetrahedron enclosing the bounding box
    return (
        Point3D(mid_x, mid_y, max_z + delta, id=-1),
        Point3D(mid_x, min_y - delta, min_z - delta, id=-2),
        Point3D(min_x - delta, max_y + delta, min_z - delta, id=-3),
        Point3D(max_x + delta, max_y + delta, min_z - delta, id=-4),
    )


def get_tet_circumcenter(v0: Point3D, v1: Point3D, v2: Point3D, v3: Point3D) -> Tuple[Point3D, float]:
    """
    Calculates the circumcenter and circumradius of a tetrahedron.
    """
    # Using the formula based on determinants
    # v1-v0, v2-v0, v3-v0
    a = v1.x - v0.x; b = v1.y - v0.y; c = v1.z - v0.z
    d = v2.x - v0.x; e = v2.y - v0.y; f = v2.z - v0.z
    g = v3.x - v0.x; h = v3.y - v0.y; i = v3.z - v0.z

    # Square lengths
    asq = a*a + b*b + c*c
    dsq = d*d + e*e + f*f
    gsq = g*g + h*h + i*i

    determinant = a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)

    if abs(determinant) < 1e-12:
        # Degenerate case, return centroid
        return Point3D((v0.x+v1.x+v2.x+v3.x)/4, (v0.y+v1.y+v2.y+v3.y)/4, (v0.z+v1.z+v2.z+v3.z)/4), 0.0

    denominator = 2.0 * determinant

    cx = (asq*(e*i - f*h) - b*(dsq*i - f*gsq) + c*(dsq*h - e*gsq)) / denominator
    cy = (a*(dsq*i - f*gsq) - asq*(d*i - f*g) + c*(d*gsq - dsq*g)) / denominator
    cz = (a*(e*gsq - dsq*h) - b*(d*gsq - dsq*g) + asq*(d*h - e*g)) / denominator

    circumcenter = Point3D(v0.x + cx, v0.y + cy, v0.z + cz)
    circumradius = math.sqrt(cx*cx + cy*cy + cz*cz)

    return circumcenter, circumradius