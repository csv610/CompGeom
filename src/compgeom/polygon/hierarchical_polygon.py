"""Hierarchical representation of a convex polygon for multi-scale optimization."""
from __future__ import annotations
import numpy as np
from typing import List, Tuple

from compgeom.kernel import Point2D

class HierarchicalPolygon:
    """
    Represents a convex polygon at multiple levels of detail.
    Used by the Chan-Hair maximum overlap algorithm.
    """
    def __init__(self, vertices: List[Point2D], max_levels: int = 5):
        self.full_vertices = vertices
        self.levels: List[List[Point2D]] = [vertices]
        self._build_hierarchy(max_levels)

    def _build_hierarchy(self, max_levels: int):
        """Constructs coarser versions of the polygon."""
        curr = self.full_vertices
        for _ in range(max_levels - 1):
            if len(curr) <= 4:
                break
            # Pick every second vertex to halve the complexity
            # Note: For convex polygons, any subset of vertices remains convex.
            next_level = curr[::2]
            self.levels.append(next_level)
            curr = next_level
            
        # Reverse so level 0 is coarsest
        self.levels.reverse()

    def get_level(self, level: int) -> List[Point2D]:
        """Returns the vertices at the specified level (0 = coarsest)."""
        idx = min(level, len(self.levels) - 1)
        return self.levels[idx]

    @property
    def num_levels(self) -> int:
        return len(self.levels)
