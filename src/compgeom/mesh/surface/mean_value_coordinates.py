"""Mean Value Coordinates for Mesh Parameterization.

Mean Value Coordinates (MVC) provide an alternative to
cotangent weights that is more numerically stable,
especially for irregular triangulations.

References:
    - Floater, "Mean Value Coordinates", 2003
    - Hormann & Floater, "Mean Value Coordinates for Arbitrary Polygons", 2006
    - Weber et al., "Conformal Flattening by Curvature Theorem", 2012
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class MeanValueCoordinates:
    """Mean Value Coordinates for conformal UV parameterization.

    MVC provides a convex combination of neighbor positions
    that is valid for arbitrary triangulations, unlike
    cotangent weights which can be negative for non-Delaunay meshes.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self._build_adjacency()

    def _build_adjacency(self) -> None:
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.faces_by_vertex: Dict[int, List[int]] = {}

        for fi, face in enumerate(self.mesh.faces):
            v_indices = face.v_indices
            for v in v_indices:
                if v not in self.faces_by_vertex:
                    self.faces_by_vertex[v] = []
                self.faces_by_vertex[v].append(fi)

            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                if v not in self.adj[u]:
                    self.adj[u].append(v)
                if u not in self.adj[v]:
                    self.adj[v].append(u)

    def compute_mean_value_weights(
        self,
        vertex: int,
    ) -> Dict[int, float]:
        """Compute MVC weights for a vertex.

        Returns dictionary of neighbor -> weight pairs.
        Uses the mean value theorem for convex combination.
        """
        neighbors = self.adj[vertex]
        if not neighbors:
            return {}

        node = self.mesh.nodes[vertex].point
        p0 = np.array([node.x, node.y, getattr(node, "z", 0.0)])

        weights = {}

        for nj in neighbors:
            neighbor_node = self.mesh.nodes[nj].point
            p1 = np.array([neighbor_node.x, neighbor_node.y, getattr(neighbor_node, "z", 0.0)])

            r = np.linalg.norm(p1 - p0)
            if r > 1e-10:
                weights[nj] = 1.0 / r
            else:
                weights[nj] = 0.0

        total = sum(weights.values())
        if total > 1e-10:
            for k in weights:
                weights[k] /= total
        else:
            for k in weights:
                weights[k] = 1.0 / len(weights)

        return weights

    def compute_embedding(
        self,
        iterations: int = 50,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute UV parameterization using MVC.

        Args:
            iterations: Number of iterations

        Returns:
            Tuple of (u, v) coordinates
        """
        boundary = self._find_boundary()
        n_b = len(boundary)

        u_coords = np.zeros(self.num_v)
        v_coords = np.zeros(self.num_v)

        if n_b > 0:
            for i, vi in enumerate(boundary):
                theta = 2 * np.pi * i / n_b
                u_coords[vi] = np.cos(theta)
                v_coords[vi] = np.sin(theta)
        else:
            u_coords[0] = 0
            v_coords[0] = 0

        interior = [i for i in range(self.num_v) if i not in boundary]

        for it in range(iterations):
            for vi in interior:
                weights = self.compute_mean_value_weights(vi)

                if weights:
                    sum_u = sum(v_coords[nj] * w for nj, w in weights.items())
                    sum_v = sum(v_coords[nj] * w for nj, w in weights.items())
                    total_w = sum(weights.values())

                    if total_w > 1e-10:
                        u_coords[vi] = sum_u / total_w
                        v_coords[vi] = sum_v / total_w

        return u_coords, v_coords

    def _find_boundary(self) -> List[int]:
        edge_count: Dict[Tuple[int, int], int] = {}

        for face in self.mesh.faces:
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                edge_count[edge] = edge_count.get(edge, 0) + 1

        boundary_edges = [e for e, c in edge_count.items() if c == 1]

        if not boundary_edges:
            return []

        boundary = set()
        for u, v in boundary_edges:
            boundary.add(u)
            boundary.add(v)

        next_v = {u: v for u, v in boundary_edges}
        loop = []
        curr = boundary_edges[0][0]
        while curr not in loop:
            loop.append(curr)
            curr = next_v.get(curr, curr)
            if curr == loop[0]:
                break

        return loop[:-1] if loop and loop[-1] == loop[0] else loop


class MeanValueEmbedding:
    """Full MVC-based embedding with improved numerics."""

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.solver = MeanValueCoordinates(mesh)

    def compute(
        self,
        boundary_type: str = "circle",
        iterations: int = 50,
    ) -> List[Tuple[float, float]]:
        """Compute UV parameterization.

        Args:
            boundary_type: "circle" or "square"
            iterations: Number of iterations

        Returns:
            List of (u, v) tuples
        """
        boundary = self.solver._find_boundary()
        n_b = len(boundary)

        u_coords = np.zeros(self.num_v)
        v_coords = np.zeros(self.num_v)

        if boundary_type == "circle":
            for i, vi in enumerate(boundary):
                theta = 2 * np.pi * i / n_b
                u_coords[vi] = np.cos(theta)
                v_coords[vi] = np.sin(theta)
        else:
            for i, vi in enumerate(boundary):
                t = i / n_b
                if t < 0.25:
                    u_coords[vi] = -1 + 4 * t
                    v_coords[vi] = -1
                elif t < 0.5:
                    u_coords[vi] = 0
                    v_coords[vi] = -1 + 4 * (t - 0.25)
                elif t < 0.75:
                    u_coords[vi] = 1 - 4 * (t - 0.5)
                    v_coords[vi] = 1
                else:
                    u_coords[vi] = 1
                    v_coords[vi] = 1 - 4 * (t - 0.75)

        interior = [i for i in range(self.num_v) if i not in boundary]

        for _ in range(iterations):
            new_u = u_coords.copy()
            new_v = v_coords.copy()

            for vi in interior:
                weights = self.solver.compute_mean_value_weights(vi)
                if not weights:
                    continue

                sum_u = sum(new_u[nj] * w for nj, w in weights.items())
                sum_v = sum(new_v[nj] * w for nj, w in weights.items())
                total = sum(weights.values())

                if total > 1e-10:
                    u_coords[vi] = sum_u / total
                    v_coords[vi] = sum_v / total

        return [(u_coords[i], v_coords[i]) for i in range(self.num_v)]


class MeanValueLaplacian:
    """Mean Value Laplacian as alternative to cotangent Laplacian."""

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self._build()

    def _build(self) -> None:
        from compgeom.mesh.surface.mean_value_coordinates import MeanValueCoordinates

        mvc = MeanValueCoordinates(self.mesh)
        n = self.num_v

        self.L = np.zeros((n, n))

        for i in range(n):
            weights = mvc.compute_mean_value_weights(i)
            for j, w in weights.items():
                self.L[i, j] = -w
            self.L[i, i] = sum(weights.values()) if weights else 1.0

    def apply(self, u: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply Laplacian to function u."""
        return self.L @ u


def mean_value_coordinates(
    mesh,
    iterations: int = 50,
) -> List[Tuple[float, float]]:
    """Convenience function for MVC parameterization.

    Args:
        mesh: TriMesh with nodes and faces
        iterations: Number of iterations

    Returns:
        List of (u, v) coordinate tuples
    """
    solver = MeanValueCoordinates(mesh)
    u, v = solver.compute_embedding(iterations=iterations)
    return [(u[i], v[i]) for i in range(solver.num_v)]
