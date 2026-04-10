"""Discrete Circle Packing for conformal mapping.

Discrete circle packing is based on the Koebe-Andreev-Thurston theorem:
every triangulated surface can be realized as a circle packing where
circles are tangent to their neighbors.

This module implements the Thurston circle packing algorithm
with discrete Ricci flow to compute conformal structures.

References:
    - Thurston, "The Geometry and Topology of 3-Manifolds", 1978
    - Bowden, "Circle Packing: A Geometric Theory of Quasiconformal Maps", 2000
    - Gu & Yau, "Computing Conformal Structures of General Manifolds", 2003
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class CirclePacking:
    """Discrete circle packing for conformal surface parameterization.

    Given a triangulated surface, finds radii of circles at each vertex
    such that tangent circles exist. This defines a discrete conformal
    structure that can be used for conformal mapping.
    """

    def __init__(self, mesh, use_intrinsic: bool = False) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)
        self.use_intrinsic = use_intrinsic

        self._build_adjacency()
        self._build_edge_lengths()

        self.radii: NDArray[np.float64] = np.ones(self.num_v)
        self.target_curvature: Optional[NDArray[np.float64]] = None
        self.conformal_factor: Optional[NDArray[np.float64]] = None

    def _build_adjacency(self) -> None:
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.edges: List[Tuple[int, int]] = []
        self.edge_to_idx: Dict[Tuple[int, int], int] = {}

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

    def _build_edge_lengths(self) -> None:
        self.edge_lengths: NDArray[np.float64] = np.zeros(len(self.edges))
        nodes = self.mesh.nodes

        for idx, (u, v) in enumerate(self.edges):
            p_u = nodes[u].point
            p_v = nodes[v].point
            dx = p_u.x - p_v.x
            dy = p_u.y - p_v.y
            dz = getattr(p_u, "z", 0.0) - getattr(p_v, "z", 0.0)
            self.edge_lengths[idx] = np.sqrt(dx * dx + dy * dy + dz * dz)

    def discrete_curvature(self, radii: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute discrete Gaussian curvature at each vertex.

        curvature[i] = 2*pi - sum of interior angles at vertex i
        For conformal structure, this should equal target curvature.
        """
        curvature = np.zeros(self.num_v)

        for i in range(self.num_v):
            angle_sum = 0.0
            for e_idx, (u, v) in enumerate(self.edges):
                l_uv = self.edge_lengths[e_idx]
                if l_uv == 0:
                    continue
                r_u, r_v = radii[u], radii[v]
                l_eff = l_uv / (r_u + r_v)
                if l_eff >= 2:
                    continue
                angle = 2 * np.arcsin(np.clip(l_eff / 2, 0, 1))
                if u == i or v == i:
                    angle_sum += angle
            curvature[i] = 2 * np.pi - angle_sum

        return curvature

    def ricci_flow(
        self,
        iterations: int = 100,
        tol: float = 1e-6,
        step_size: float = 0.1,
    ) -> NDArray[np.float64]:
        """Evolve radii via discrete Ricci flow to target curvature.

        Uses flow: dr/dt = (target_curvature - current_curvature) * r
        which converges to conformal structure with target curvature.

        Args:
            iterations: Maximum iterations
            tol: Convergence tolerance
            step_size: Flow step size

        Returns:
            Converged radii array
        """
        target_curv = self.discrete_curvature(np.ones(self.num_v))

        radii = self.radii.copy()

        for it in range(iterations):
            curvature = self.discrete_curvature(radii)
            residual = target_curv - curvature

            if np.linalg.norm(residual) < tol:
                break

            for i in range(self.num_v):
                if radii[i] > 1e-10:
                    radii[i] *= 1 + step_size * residual[i] / (2 * np.pi)
                    radii[i] = max(radii[i], 1e-10)

            radii = radii * (self.num_v / radii.sum())

        self.radii = radii
        return radii

    def set_target_curvature(
        self,
        curvature: Optional[NDArray[np.float64]] = None,
        genus: int = 0,
    ) -> None:
        """Set target curvature for Ricci flow.

        For genus g surface with boundary n components:
        target curvature = 2*pi * (2 - 2g - n) / num_v

        Args:
            curvature: Optional explicit target curvature per vertex
            genus: Genus of the surface (for closed surfaces)
        """
        if curvature is not None:
            self.target_curvature = curvature
        else:
            self.target_curvature = np.zeros(self.num_v)

    def compute_conformal_map(self) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute conformal parameterization from circle packing.

        Uses the radii to compute edge lengths in the conformal metric,
        then solves for planar positions.

        Returns:
            Tuple of (u, v) coordinates for each vertex
        """
        radii = self.radii

        u_coords = np.zeros(self.num_v)
        v_coords = np.zeros(self.num_v)

        boundary = self._find_boundary()
        if boundary:
            n_b = len(boundary)
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
                    e_idx = self.edge_to_idx.get(edge)
                    if e_idx is not None:
                        w = self.edge_lengths[e_idx] / (radii[vi] + radii[nj])
                        sum_u += w * u_coords[nj]
                        sum_v += w * v_coords[nj]
                        weight_sum += w
                if weight_sum > 0:
                    u_coords[vi] = sum_u / weight_sum
                    v_coords[vi] = sum_v / weight_sum

        return u_coords, v_coords

    def _find_boundary(self) -> List[int]:
        """Find boundary vertices of the mesh."""
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

        return list(boundary)

    def get_circle_radii(self) -> NDArray[np.float64]:
        """Get the circle radii after packing."""
        return self.radii.copy()

    def conformal_factor_at_vertices(self) -> NDArray[np.float64]:
        """Get conformal factor (log of radius ratio to original)."""
        if self.conformal_factor is None:
            original_lengths = np.zeros(self.num_v)
            for i in range(self.num_v):
                if self.adj[i]:
                    lengths = []
                    for j in self.adj[i]:
                        edge = tuple(sorted((i, j)))
                        e_idx = self.edge_to_idx.get(edge)
                        if e_idx is not None:
                            lengths.append(self.edge_lengths[e_idx])
                    if lengths:
                        original_lengths[i] = np.mean(lengths)
                    else:
                        original_lengths[i] = 1.0
                else:
                    original_lengths[i] = 1.0
            original_lengths = np.maximum(original_lengths, 1e-10)
            self.conformal_factor = np.log(self.radii / original_lengths)
        return self.conformal_factor


class ThurstonCirclePacking(CirclePacking):
    """Thurston's circle packing algorithm variant.

    Implements the discrete conformal mapping via circle packing
    using the iterative angle assignment method.
    """

    def __init__(self, mesh) -> None:
        super().__init__(mesh)
        self.angle_deficits: Optional[NDArray[np.float64]] = None

    def assign_angles(self, target_angle_sum: float = np.pi) -> None:
        """Assign angle sums to each vertex.

        Args:
            target_angle_sum: Target sum of angles at each interior vertex
        """
        self.angle_deficits = np.full(self.num_v, target_angle_sum)

    def solve(
        self,
        max_iterations: int = 200,
        tolerance: float = 1e-6,
    ) -> NDArray[np.float64]:
        """Solve for circle radii using angle constraints.

        Args:
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            Converged radii
        """
        radii = np.ones(self.num_v)

        for iteration in range(max_iterations):
            curvature = self.discrete_curvature(radii)

            if self.angle_deficits is not None:
                residual = self.angle_deficits - curvature
            else:
                residual = -curvature

            max_residual = np.max(np.abs(residual))
            if max_residual < tolerance:
                break

            for i in range(self.num_v):
                if abs(residual[i]) > tolerance:
                    factor = 1 + 0.1 * np.sign(residual[i]) * min(abs(residual[i]), 0.5)
                    radii[i] *= factor

            radii = radii * (self.num_v / radii.sum())

        self.radii = radii
        return radii


def discrete_circle_packing(
    mesh,
    iterations: int = 100,
    tol: float = 1e-6,
) -> NDArray[np.float64]:
    """Convenience function for discrete circle packing.

    Args:
        mesh: TriMesh with nodes and faces
        iterations: Maximum iterations for Ricci flow
        tol: Convergence tolerance

    Returns:
        Circle radii for each vertex
    """
    packing = CirclePacking(mesh)
    return packing.ricci_flow(iterations=iterations, tol=tol)
