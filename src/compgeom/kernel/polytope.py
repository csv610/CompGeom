"""High-dimensional polytope engine for geometric discovery."""
from __future__ import annotations
import numpy as np
from scipy.spatial import ConvexHull
from typing import List, Set, Tuple, Optional, Dict
from collections import deque

class HighDimPolytope:
    """
    Represents a convex polytope in d-dimensional space.
    Uses scipy.spatial.ConvexHull for topology computation.
    """
    def __init__(self, points: np.ndarray):
        """
        points: (N, d) array of point coordinates.
        """
        self.points = points
        self._hull: Optional[ConvexHull] = None
        self._compute_hull()

    def _compute_hull(self):
        """Computes the convex hull of the current points."""
        if len(self.points) < self.dim + 1:
            self._hull = None
            return
        try:
            self._hull = ConvexHull(self.points)
        except Exception:
            self._hull = None

    @property
    def dim(self) -> int:
        return self.points.shape[1]

    @property
    def num_vertices(self) -> int:
        return len(self._hull.vertices) if self._hull else 0

    @property
    def num_facets(self) -> int:
        """Returns the number of non-coplanar facets."""
        if not self._hull:
            return 0
        # Group simplices by their normal equations to find unique facets
        # equations is (N_simplices, d+1)
        unique_facets = []
        for eq in self._hull.equations:
            is_new = True
            for u_eq in unique_facets:
                # Compare normals and offsets with a tolerance
                if np.allclose(eq, u_eq, atol=1e-6):
                    is_new = False
                    break
            if is_new:
                unique_facets.append(eq)
        return len(unique_facets)

    def get_diameter(self) -> int:
        """
        Computes the diameter of the vertex-edge graph.
        An edge exists between two vertices if they share at least d-1 facets.
        """
        if not self._hull:
            return 0
            
        d = self.dim
        vertices = self._hull.vertices
        simplices = self._hull.simplices
        equations = self._hull.equations
        
        # 1. Map each vertex to the set of facets it belongs to
        # First, identify unique facets (group coplanar simplices)
        facet_map = [] # List of unique (normal, offset)
        simplex_to_facet = {}
        for i, eq in enumerate(equations):
            found = False
            for j, u_eq in enumerate(facet_map):
                if np.allclose(eq, u_eq, atol=1e-6):
                    simplex_to_facet[i] = j
                    found = True
                    break
            if not found:
                simplex_to_facet[i] = len(facet_map)
                facet_map.append(eq)
        
        vertex_facets = {v: set() for v in vertices}
        for i, simplex in enumerate(simplices):
            f_idx = simplex_to_facet[i]
            for v in simplex:
                vertex_facets[v].add(f_idx)
                
        # 2. Build adjacency list
        # Two vertices share an edge if they share d-1 facets
        neighbors = {v: set() for v in vertices}
        v_list = list(vertices)
        for i in range(len(v_list)):
            for j in range(i + 1, len(v_list)):
                u, v = v_list[i], v_list[j]
                common = vertex_facets[u].intersection(vertex_facets[v])
                if len(common) >= d - 1:
                    neighbors[u].add(v)
                    neighbors[v].add(u)
                    
        # 3. BFS for all-pairs shortest paths
        max_dist = 0
        for start_v in v_list:
            distances = {v: -1 for v in v_list}
            distances[start_v] = 0
            q = deque([start_v])
            while q:
                u = q.popleft()
                dist = distances[u]
                if dist > max_dist: max_dist = dist
                for neighbor in neighbors[u]:
                    if distances[neighbor] == -1:
                        distances[neighbor] = dist + 1
                        q.append(neighbor)
        return max_dist

    def mutate_perturb(self, sigma: float = 0.01):
        """Randomly perturbs the positions of existing vertices."""
        noise = np.random.normal(0, sigma, self.points.shape)
        self.points += noise
        self._compute_hull()

    def add_point(self, p: np.ndarray):
        """Adds a new point to the set and updates the hull."""
        self.points = np.vstack([self.points, p.reshape(1, -1)])
        self._compute_hull()

    def prune_redundant(self):
        """Removes points that are not vertices of the convex hull."""
        if self._hull:
            self.points = self.points[self._hull.vertices]
            self._compute_hull()
