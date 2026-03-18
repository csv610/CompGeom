"""Shared utilities for Delaunay triangulation algorithms."""

from __future__ import annotations
import math
from typing import Iterable, TYPE_CHECKING, Tuple

from compgeom.kernel import Point2D, hilbert_key


if TYPE_CHECKING:
    from compgeom.mesh.surfmesh.trimesh.delaunay_mesh_edgeflip import EdgeFlipTriangle
    from compgeom.mesh.surfmesh.trimesh.delaunay_mesh_incremental import IncrementalTriangle

class PointGrid:
    """Simple 2D grid for fast nearest-neighbor search."""
    def __init__(self, points: Iterable[Point2D]):
        pts = list(points)
        if not pts:
            self.min_x = self.max_x = self.min_y = self.max_y = 0.0
            self.grid = {}
            self.cell_size = 1.0
            self.num_cells = 1
            return

        self.min_x = min(p.x for p in pts)
        self.max_x = max(p.x for p in pts)
        self.min_y = min(p.y for p in pts)
        self.max_y = max(p.y for p in pts)
        
        n = len(pts)
        self.num_cells = int(math.sqrt(n)) + 1
        self.cell_size = max((self.max_x - self.min_x) / self.num_cells, 
                             (self.max_y - self.min_y) / self.num_cells, 
                             0.1)
        
        self.grid: dict[tuple[int, int], list[Point2D]] = {}

    def _get_cell(self, p: Point2D) -> tuple[int, int]:
        return (int((p.x - self.min_x) / self.cell_size), 
                int((p.y - self.min_y) / self.cell_size))

    def add(self, p: Point2D):
        cell = self._get_cell(p)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(p)

    def find_nearest(self, p: Point2D) -> Point2D | None:
        """Finds the nearest point in the grid to point p."""
        if not self.grid:
            return None
            
        cx, cy = self._get_cell(p)
        nearest = None
        min_dist_sq = float('inf')
        
        radius = 0
        while not nearest and radius < self.num_cells:
            for i in range(cx - radius, cx + radius + 1):
                for j in range(cy - radius, cy + radius + 1):
                    if abs(i - cx) != radius and abs(j - cy) != radius:
                        continue
                    cell_points = self.grid.get((i, j))
                    if cell_points:
                        for cp in cell_points:
                            dist_sq = (p.x - cp.x)**2 + (p.y - cp.y)**2
                            if dist_sq < min_dist_sq:
                                min_dist_sq = dist_sq
                                nearest = cp
            radius += 1
        return nearest


def create_super_triangle(points: Iterable[Point2D], scale: float = 100.0) -> tuple[Point2D, Point2D, Point2D]:
    """Creates a super-triangle that encloses all given points."""
    pts = list(points)
    if not pts:
        return (Point2D(0, 100, id=-1), Point2D(-100, -100, id=-2), Point2D(100, -100, id=-3))
        
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    dx = max_x - min_x
    dy = max_y - min_y
    delta = max(dx, dy, 1.0) * scale
    mid_x = (min_x + max_x) / 2
    
    return (
        Point2D(mid_x, max_y + delta, id=-1),
        Point2D(min_x - delta, min_y - delta, id=-2),
        Point2D(max_x + delta, min_y - delta, id=-3),
    )
