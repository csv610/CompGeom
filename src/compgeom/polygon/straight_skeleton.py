from __future__ import annotations
import heapq
import math
from typing import List, Tuple, Dict, Set, Optional
from compgeom.kernel.point import Point2D
from compgeom.kernel.polygon import Polygon2D

class StraightSkeleton:
    """
    Computes the Straight Skeleton of a polygon using wavefront propagation.
    """
    def __init__(self, polygon: Polygon2D):
        self.polygon = polygon
        self.skeleton_points: List[Point2D] = list(polygon.vertices)
        self.skeleton_edges: List[Tuple[int, int]] = []
        
    def compute(self):
        """
        Computes the skeleton by simulating an inward-moving wavefront.
        """
        # 1. Initialize wavefront
        # Each vertex moves along the bisector of its adjacent edges
        bisectors = self._compute_bisectors()
        
        # 2. Priority queue of events (Edge collapse or Split)
        # Simplified: Compute potential collapse time for each edge
        events = []
        n = len(self.polygon.vertices)
        for i in range(n):
            t = self._compute_collision_time(i, (i+1)%n, bisectors)
            if t > 0:
                heapq.heappush(events, (t, i, (i+1)%n))
        
        # 3. Process first few events to demonstrate the skeleton structure
        processed = set()
        while events and len(self.skeleton_edges) < n - 2:
            t, i, j = heapq.heappop(events)
            if i in processed or j in processed: continue
            
            # Create a new skeleton point at the collision site
            new_p = self._get_collision_point(i, j, bisectors, t)
            new_idx = len(self.skeleton_points)
            self.skeleton_points.append(new_p)
            
            self.skeleton_edges.append((i, new_idx))
            self.skeleton_edges.append((j, new_idx))
            
            processed.update([i, j])
            
    def _compute_bisectors(self) -> List[Tuple[float, float]]:
        """
        Compute the inward angular bisector direction for each vertex.
        Returns list of (dx, dy) normalized direction vectors.
        """
        n = len(self.polygon.vertices)
        bisectors = []

        for i in range(n):
            prev_idx = (i - 1) % n
            next_idx = (i + 1) % n
            v_prev = self.polygon.vertices[prev_idx]
            v_curr = self.polygon.vertices[i]
            v_next = self.polygon.vertices[next_idx]

            # Edge vectors (inward direction)
            e1x = v_prev.x - v_curr.x
            e1y = v_prev.y - v_curr.y
            e2x = v_next.x - v_curr.x
            e2y = v_next.y - v_curr.y

            # Normalize edge vectors
            len1 = math.hypot(e1x, e1y)
            len2 = math.hypot(e2x, e2y)
            if len1 == 0 or len2 == 0:
                bisectors.append((0.0, 0.0))
                continue

            e1x, e1y = e1x / len1, e1y / len1
            e2x, e2y = e2x / len2, e2y / len2

            # Angle bisector direction (inward for CCW polygons)
            # For CCW: rotate edge vectors 90 degrees CCW to get outward normals
            # Then bisector is sum of inward edge directions
            bisector_x = -e1x - e2x
            bisector_y = -e1y - e2y

            # Normalize
            bisector_len = math.hypot(bisector_x, bisector_y)
            if bisector_len > 0:
                bisector_x /= bisector_len
                bisector_y /= bisector_len

            bisectors.append((bisector_x, bisector_y))

        return bisectors

    def _compute_collision_time(self, i: int, j: int, bisectors: List[Tuple[float, float]]) -> float:
        """
        Compute the time when edge (i,j) collapses.
        Edge collapses when vertices i and j moving along bisectors meet.
        """
        if not bisectors or i >= len(bisectors) or j >= len(bisectors):
            return -1.0

        vi = self.polygon.vertices[i]
        vj = self.polygon.vertices[j]
        bi = bisectors[i]
        bj = bisectors[j]

        # Vertex positions at time t: vi + t*bi, vj + t*bj
        # Collision when: vi + t*bi = vj + t*bj
        # => vi - vj = t*(bj - bi)
        # Solve for t using least squares
        dx = vi.x - vj.x
        dy = vi.y - vj.y
        dbx = bj[0] - bi[0]
        dby = bj[1] - bi[1]

        denom = dbx * dbx + dby * dby
        if denom == 0:
            return -1.0  # Parallel bisectors

        # Project displacement onto bisector difference
        t = -(dx * dbx + dy * dby) / denom

        return t if t > 0 else -1.0

    def _get_collision_point(self, i: int, j: int, bisectors: List[Tuple[float, float]], t: float) -> Point2D:
        """Compute the collision point at time t."""
        vi = self.polygon.vertices[i]
        bi = bisectors[i]
        return Point2D(vi.x + t * bi[0], vi.y + t * bi[1])
