"""Tutte Embedding with Cotangent Weights for Conformal Parameterization.

Tutte's embedding theorem states that a planar graph can be embedded in the plane
such that each vertex's position is a weighted average of its neighbors.
Using cotangent weights gives a discrete conformal Laplacian (Laplace-Beltrami
operator on triangulated surfaces), producing low-distortion conformal maps.

References:
    - Tutte, "How to Draw a Graph", 1963
    - Desbrun et al., "Implicit Fairing of Triangle Meshes", 1999
    - Levy et al., "Spectral Conformal Parameterization", 2002
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class TutteEmbedding:
    """Tutte embedding with cotangent weights for conformal UV parameterization.

    This class implements the classic Tutte embedding using cotangent weights
    to compute a conformal parameterization of a triangulated surface.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self._build_adjacency()
        self._build_cotan_weights()

    def _build_adjacency(self) -> None:
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.edge_to_idx: Dict[Tuple[int, int], int] = {}
        self.edges: List[Tuple[int, int]] = []

        for face in self.mesh.faces:
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                if edge not in self.edge_to_idx:
                    self.edge_to_idx[edge] = len(self.edges)
                    self.edges.append(edge)
                    self.adj[u].append(v)
                    self.adj[v].append(u)

    def _build_cotan_weights(self) -> None:
        """Build cotangent weights for each edge.

        Cotangent weight for edge (i,j) is sum of cotangents of opposite angles
        in the two triangles sharing that edge.
        """
        nodes = self.mesh.nodes
        self.cotan_weights: NDArray[np.float64] = np.zeros(len(self.edges))

        for face in self.mesh.faces:
            v0, v1, v2 = face.v_indices
            p0 = np.array([nodes[v0].point.x, nodes[v0].point.y, getattr(nodes[v0].point, "z", 0.0)])
            p1 = np.array([nodes[v1].point.x, nodes[v1].point.y, getattr(nodes[v1].point, "z", 0.0)])
            p2 = np.array([nodes[v2].point.x, nodes[v2].point.y, getattr(nodes[v2].point, "z", 0.0)])

            v_list = [v0, v1, v2]
            p_list = [p0, p1, p2]

            for k in range(3):
                i, j, opp = v_list[k], v_list[(k + 1) % 3], v_list[(k + 2) % 3]
                p_i, p_j, p_opp = p_list[k], p_list[(k + 1) % 3], p_list[(k + 2) % 3]

                edge = tuple(sorted((i, j)))
                e_idx = self.edge_to_idx[edge]
                edge_vec = p_i - p_j
                opposite_vec = p_opp - p_j

                cross = np.cross(edge_vec, opposite_vec)
                norm = np.linalg.norm(cross)
                if norm > 1e-10:
                    cot = np.dot(edge_vec, opposite_vec) / norm
                    self.cotan_weights[e_idx] += 0.5 * cot

    def compute_embedding(
        self,
        boundary_type: str = "circle",
        iterations: int = 50,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute Tutte embedding using cotangent weights.

        Solves the Laplace equation with Dirichlet boundary conditions.

        Args:
            boundary_type: "circle" (conformal) or "square" (authalic)
            iterations: Number of iterations

        Returns:
            Tuple of (u, v) coordinates
        """
        boundary = self._find_boundary()
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
            for vi in interior:
                neighbors = self.adj[vi]
                if not neighbors:
                    continue

                sum_u = sum_v = 0.0
                weight_sum = 0.0

                for nj in neighbors:
                    edge = tuple(sorted((vi, nj)))
                    e_idx = self.edge_to_idx.get(edge)
                    if e_idx is not None:
                        w = max(self.cotan_weights[e_idx], 0.0)
                        sum_u += w * u_coords[nj]
                        sum_v += w * v_coords[nj]
                        weight_sum += w

                if weight_sum > 0:
                    u_coords[vi] = sum_u / weight_sum
                    v_coords[vi] = sum_v / weight_sum

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

        boundary = set()
        for u, v in boundary_edges:
            boundary.add(u)
            boundary.add(v)

        loop = []
        if boundary_edges:
            next_v = {u: v for u, v in boundary_edges}
            curr = boundary_edges[0][0]
            while curr not in loop:
                loop.append(curr)
                curr = next_v.get(curr, curr)
                if curr == loop[0]:
                    break

        return loop[:-1] if loop and loop[-1] == loop[0] else loop

    def get_uv_coordinates(self) -> List[Tuple[float, float]]:
        """Get embedding as list of (u, v) coordinate tuples."""
        u, v = self.compute_embedding()
        return [(u[i], v[i]) for i in range(self.num_v)]

    def compute_gradient_operator(self) -> NDArray[np.float64]:
        """Compute the gradient operator matrix.

        Returns matrix G such that G @ u gives gradient of u.
        """
        n = self.num_v
        G = np.zeros((2 * len(self.edges), n))

        for e_idx, (i, j) in enumerate(self.edges):
            w = self.cotan_weights[e_idx]
            if w > 0:
                G[e_idx, i] = w
                G[e_idx, j] = -w
                G[len(self.edges) + e_idx, i] = -w
                G[len(self.edges) + e_idx, j] = w

        return G

    def compute_divergence(self, vector_field: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute divergence of a vector field on the mesh."""
        div = np.zeros(self.num_v)

        for e_idx, (i, j) in enumerate(self.edges):
            w = self.cotan_weights[e_idx]
            if w > 0:
                u_comp = vector_field[e_idx]
                v_comp = vector_field[len(self.edges) + e_idx]
                div[i] += w * (u_comp + v_comp)
                div[j] -= w * (u_comp + v_comp)

        return div


class CotangentLaplacian:
    """Discrete cotangent Laplacian (Laplace-Beltrami operator).

    Provides the cotangent Laplacian matrix for triangulated surfaces,
    used in various geometry processing tasks like smoothing,
    parameterization, and spectral analysis.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.L: Optional[NDArray[np.float64]] = None
        self._build()

    def _build(self) -> None:
        """Build the cotangent Laplacian matrix."""
        n = self.num_v
        self.L = np.zeros((n, n))

        nodes = self.mesh.nodes
        edge_weights: Dict[Tuple[int, int], float] = {}

        for face in self.mesh.faces:
            v0, v1, v2 = face.v_indices
            p0 = np.array([nodes[v0].point.x, nodes[v0].point.y, getattr(nodes[v0].point, "z", 0.0)])
            p1 = np.array([nodes[v1].point.x, nodes[v1].point.y, getattr(nodes[v1].point, "z", 0.0)])
            p2 = np.array([nodes[v2].point.x, nodes[v2].point.y, getattr(nodes[v2].point, "z", 0.0)])

            v_list = [v0, v1, v2]
            p_list = [p0, p1, p2]

            for k in range(3):
                i, j, opp = v_list[k], v_list[(k + 1) % 3], v_list[(k + 2) % 3]
                p_i, p_j, p_opp = p_list[k], p_list[(k + 1) % 3], p_list[(k + 2) % 3]

                edge = tuple(sorted((i, j)))
                edge_vec = p_i - p_j
                opposite_vec = p_opp - p_j

                cross = np.cross(edge_vec, opposite_vec)
                norm = np.linalg.norm(cross)
                if norm > 1e-10:
                    cot = np.dot(edge_vec, opposite_vec) / norm
                    edge_weights[edge] = edge_weights.get(edge, 0) + 0.5 * cot

        adj: Dict[int, List[int]] = {i: [] for i in range(n)}
        for edge, w in edge_weights.items():
            i, j = edge
            self.L[i, j] = -w
            self.L[j, i] = -w
            adj[i].append(j)
            adj[j].append(i)

        for i in range(n):
            self.L[i, i] = -np.sum(self.L[i, :])

    def apply(self, u: NDArray[np.float64]) -> NDArray[np.float64]:
        """Apply Laplacian to a function u."""
        return self.L @ u

    def solve_poisson(
        self,
        rhs: NDArray[np.float64],
        boundary_values: Optional[NDArray[np.float64]] = None,
    ) -> NDArray[np.float64]:
        """Solve Poisson equation: L @ u = rhs."""
        if boundary_values is not None:
            fixed = np.where(np.isfinite(boundary_values))[0]
            interior = np.where(~np.isfinite(boundary_values))[0]

            if len(interior) == 0:
                return boundary_values

            L_int = self.L[np.ix_(interior, interior)]
            rhs_int = rhs[interior] - self.L[np.ix_(interior, fixed)] @ boundary_values[fixed]

            u_int = np.linalg.solve(L_int, rhs_int)
            u = np.zeros(self.num_v)
            u[interior] = u_int
            u[fixed] = boundary_values[fixed]
            return u
        else:
            return np.linalg.solve(self.L + 1e-10 * np.eye(self.num_v), rhs)


def tutte_embedding(
    mesh,
    boundary_type: str = "circle",
) -> List[Tuple[float, float]]:
    """Convenience function for Tutte embedding.

    Args:
        mesh: TriMesh with nodes and faces
        boundary_type: "circle" or "square"

    Returns:
        List of (u, v) coordinate tuples
    """
    solver = TutteEmbedding(mesh)
    return solver.get_uv_coordinates()


def cotangent_laplacian(mesh) -> CotangentLaplacian:
    """Convenience function to get cotangent Laplacian."""
    return CotangentLaplacian(mesh)
