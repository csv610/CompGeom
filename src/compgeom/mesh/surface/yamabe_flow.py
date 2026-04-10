"""Discrete Yamabe Flow for Conformal Parameterization.

The discrete Yamabe flow evolves the metric by normalizing surface area
while trying to achieve constant curvature. Unlike Ricci flow which
evolves curvature directly, Yamabe flow normalizes by total area,
making it more numerically stable.

References:
    - Gu & Yau, "Computing Conformal Structures of General Manifolds", 2003
    - Jin et al., "Discrete Surface Yamabe Flow", 2008
    - Weber et al., "Conformal Flattening by Curvature Theorem", 2012
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class DiscreteYamabeFlow:
    """Discrete Yamabe flow for conformal surface parameterization.

    The Yamabe flow evolves vertex conformal factors to:
    1. Normalize total surface area
    2. Achieve constant curvature (uniform conformal factors)

    This is more stable than Ricci flow for surfaces with
    high curvature variation.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self._build_mesh_structure()

    def _build_mesh_structure(self) -> None:
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.edge_lengths: Dict[Tuple[int, int], float] = {}
        self.edge_to_idx: Dict[Tuple[int, int], int] = {}
        self.edges: List[Tuple[int, int]] = []

        nodes = self.mesh.nodes

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

                    diff = np.array(
                        [
                            nodes[u].point.x - nodes[v].point.x,
                            nodes[u].point.y - nodes[v].point.y,
                            getattr(nodes[u].point, "z", 0.0) - getattr(nodes[v].point, "z", 0.0),
                        ]
                    )
                    self.edge_lengths[edge] = np.linalg.norm(diff)

    def compute_original_area(self) -> float:
        """Compute total surface area of original mesh."""
        area = 0.0
        nodes = self.mesh.nodes

        for face in self.mesh.faces:
            v = face.v_indices
            p0 = np.array([nodes[v[0]].point.x, nodes[v[0]].point.y, getattr(nodes[v[0]].point, "z", 0.0)])
            p1 = np.array([nodes[v[1]].point.x, nodes[v[1]].point.y, getattr(nodes[v[1]].point, "z", 0.0)])
            p2 = np.array([nodes[v[2]].point.x, nodes[v[2]].point.y, getattr(nodes[v[2]].point, "z", 0.0)])

            cross = np.cross(p1 - p0, p2 - p0)
            area += 0.5 * np.linalg.norm(cross)

        return area

    def compute_discrete_curvature(self, conformal_factors: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute discrete curvature with given conformal factors.

        Uses the updated edge lengths based on conformal factors:
        l'_ij = l_ij * exp((u_i + u_j)/2)
        """
        curvature = np.zeros(self.num_v)

        for i in range(self.num_v):
            angle_sum = 0.0

            for edge, length in self.edge_lengths.items():
                u, v = edge
                if u != i and v != i:
                    continue

                j = v if u == i else u
                u_i = conformal_factors[i]
                u_j = conformal_factors[j]

                new_length = length * np.exp((u_i + u_j) / 2)

                if new_length > 1e-10:
                    angle = 2 * np.arcsin(np.clip(new_length / (length * 2 + 1e-10), 0, 1))
                    angle_sum += angle

            curvature[i] = 2 * np.pi - angle_sum

        return curvature

    def evolve(
        self,
        iterations: int = 100,
        tolerance: float = 1e-6,
        max_step: float = 0.1,
    ) -> NDArray[np.float64]:
        """Evolve conformal factors via Yamabe flow.

        The flow equation is:
        du/dt = -H + <H> (average curvature)

        With area normalization to keep total area constant.

        Args:
            iterations: Maximum iterations
            tolerance: Convergence tolerance
            max_step: Maximum step size

        Returns:
            Conformal factors (log-metric) for each vertex
        """
        original_area = self.compute_original_area()
        conformal_factors = np.zeros(self.num_v)

        for it in range(iterations):
            curvature = self.compute_discrete_curvature(conformal_factors)

            avg_curvature = np.mean(curvature)
            residual = curvature - avg_curvature

            if np.linalg.norm(residual) < tolerance:
                break

            step = max_step * np.sign(residual) * np.minimum(np.abs(residual), 1.0)
            conformal_factors += step * 0.1

        area = self._compute_current_area(conformal_factors)
        scale = np.sqrt(original_area / (area + 1e-10))
        conformal_factors += np.log(scale)

        return conformal_factors

    def _compute_current_area(self, conformal_factors: NDArray[np.float64]) -> float:
        """Compute current surface area with conformal factors."""
        area = 0.0
        nodes = self.mesh.nodes

        for face in self.mesh.faces:
            v = face.v_indices
            p0 = np.array([nodes[v[0]].point.x, nodes[v[0]].point.y, getattr(nodes[v[0]].point, "z", 0.0)])
            p1 = np.array([nodes[v[1]].point.x, nodes[v[1]].point.y, getattr(nodes[v[1]].point, "z", 0.0)])
            p2 = np.array([nodes[v[2]].point.x, nodes[v[2]].point.y, getattr(nodes[v[2]].point, "z", 0.0)])

            cross = np.cross(p1 - p0, p2 - p0)
            area += 0.5 * np.linalg.norm(cross)

        return area

    def apply_to_mesh(
        self,
        conformal_factors: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Apply conformal factors to get deformed mesh vertices.

        Returns vertex positions in the conformally deformed mesh.
        """
        nodes = self.mesh.nodes
        new_vertices = np.zeros((self.num_v, 3))

        for i, node in enumerate(nodes):
            orig = np.array([node.point.x, node.point.y, getattr(node.point, "z", 0.0)])
            new_vertices[i] = orig * np.exp(conformal_factors[i])

        return new_vertices

    def compute_conformal_map(
        self,
        iterations: int = 100,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute conformal parameterization using Yamabe flow.

        Args:
            iterations: Number of flow iterations

        Returns:
            Tuple of (u, v) coordinates
        """
        conformal_factors = self.evolve(iterations=iterations)

        return self._compute_uv_from_factors(conformal_factors)

    def _compute_uv_from_factors(
        self, conformal_factors: NDArray[np.float64]
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute UV coordinates from conformal factors."""
        boundary = self._find_boundary()

        u_coords = np.zeros(self.num_v)
        v_coords = np.zeros(self.num_v)

        n_b = len(boundary)
        if n_b > 0:
            for i, vi in enumerate(boundary):
                theta = 2 * np.pi * i / n_b
                u_coords[vi] = np.cos(theta)
                v_coords[vi] = np.sin(theta)

        interior = [i for i in range(self.num_v) if i not in boundary]

        for _ in range(50):
            for vi in interior:
                neighbors = self.adj[vi]
                if not neighbors:
                    continue

                sum_u = sum_v = 0.0
                weight_sum = 0.0

                for nj in neighbors:
                    edge = tuple(sorted((vi, nj)))
                    length = self.edge_lengths.get(edge, 1.0)
                    factor = np.exp((conformal_factors[vi] + conformal_factors[nj]) / 2)

                    sum_u += u_coords[nj] * length * factor
                    sum_v += v_coords[nj] * length * factor
                    weight_sum += length * factor

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

        if not boundary_edges:
            return []

        boundary = set()
        for u, v in boundary_edges:
            boundary.add(u)
            boundary.add(v)

        return list(boundary)


class YamabeFlowParameterization:
    """Wrapper for Yamabe flow-based parameterization."""

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.solver = DiscreteYamabeFlow(mesh)

    def compute(
        self,
        iterations: int = 100,
    ) -> List[Tuple[float, float]]:
        """Compute UV parameterization using Yamabe flow.

        Args:
            iterations: Number of flow iterations

        Returns:
            List of (u, v) coordinate tuples
        """
        u, v = self.solver.compute_conformal_map(iterations=iterations)
        return [(u[i], v[i]) for i in range(self.solver.num_v)]


def yamabe_flow(
    mesh,
    iterations: int = 100,
) -> List[Tuple[float, float]]:
    """Convenience function for Yamabe flow parameterization.

    Args:
        mesh: TriMesh with nodes and faces
        iterations: Number of flow iterations

    Returns:
        List of (u, v) coordinate tuples
    """
    solver = DiscreteYamabeFlow(mesh)
    u, v = solver.compute_conformal_map(iterations=iterations)
    return [(u[i], v[i]) for i in range(solver.num_v)]
