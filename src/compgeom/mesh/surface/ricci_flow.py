"""Combinatorial Ricci Flow for prescribed curvature on surface meshes."""

from __future__ import annotations
import numpy as np
import math
from scipy.optimize import minimize
from typing import List, Tuple, Dict, Optional, Set

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh


class RicciFlow:
    """
    Implements Combinatorial Ricci Flow to achieve target vertex curvatures.
    Chow and Luo, "Combinatorial Ricci flow on surfaces", 2003.
    """

    def __init__(self, mesh: TriMesh):
        self.mesh = mesh
        self.he_mesh = HalfEdgeMesh.from_triangle_mesh(mesh)
        self.num_v = len(mesh.vertices)
        # Initial radii (all 1.0)
        self.u = np.zeros(self.num_v)  # u_i = log(r_i)

    def solve(
        self, target_curvatures: Optional[np.ndarray] = None, max_iter: int = 100
    ) -> np.ndarray:
        """
        Evolves the conformal factors u to reach target_curvatures.
        If target_curvatures is None, it aims for zero curvature (flatness) for interior vertices.
        """
        if target_curvatures is None:
            # Default: 0 for interior, appropriate for boundary (Gauss-Bonnet)
            target_curvatures = np.zeros(self.num_v)
            # Find boundary vertices
            boundary_v = self._get_boundary_vertices()
            if boundary_v:
                # Sum of target curvatures must be 2*pi * EulerCharacteristic
                target_curvatures[list(boundary_v)] = 2 * math.pi / len(boundary_v)

        def objective(u):
            # Energy function whose gradient is (target_K - current_K)
            curvatures, _ = self._compute_curvatures(u)
            # Gradient is K_target - K_curr
            # We minimize integral energy.
            # In practice, we use a simple gradient descent or Newton's method.
            return np.sum((curvatures - target_curvatures) ** 2)

        # Use a robust optimizer
        res = minimize(
            objective, self.u, method="L-BFGS-B", options={"maxiter": max_iter}
        )
        self.u = res.x
        return self.u

    def get_edge_lengths(self) -> Dict[Tuple[int, int], float]:
        """Returns the new edge lengths after the flow."""
        lengths = {}
        for he in self.he_mesh.edges:
            u, v = he.vertex.idx, he.next.vertex.idx
            # Circle Packing model: l_uv = r_u + r_v = exp(u_u) + exp(u_v)
            l = math.exp(self.u[u]) + math.exp(self.u[v])
            lengths[tuple(sorted((u, v)))] = l
        return lengths

    def _compute_curvatures(
        self, u: np.ndarray
    ) -> Tuple[np.ndarray, Dict[int, List[float]]]:
        """Calculates current vertex curvatures K_i."""
        angles = np.zeros(self.num_v)

        # For each triangle, compute angles using new edge lengths
        for face in self.mesh.faces:
            v_idx = face.v_indices
            # Edge lengths: l_01, l_12, l_20
            l = [
                math.exp(u[v_idx[i]]) + math.exp(u[v_idx[(i + 1) % 3]])
                for i in range(3)
            ]

            # Law of Cosines for angles
            for i in range(3):
                # Angle at v_i
                a, b, c = (
                    l[i],
                    l[(i + 1) % 3],
                    l[(i + 2) % 3],
                )  # a is opposite to v_i? No.
                # Let's be precise:
                # v0, v1, v2.
                # sides: s0 (v1-v2), s1 (v2-v0), s2 (v0-v1)
                s2 = l[0]  # v0-v1
                s0 = l[1]  # v1-v2
                s1 = l[2]  # v2-v0

                # Angle at v0: cos(theta0) = (s1^2 + s2^2 - s0^2) / (2 * s1 * s2)
                # Angle at v1: cos(theta1) = (s2^2 + s0^2 - s1^2) / (2 * s2 * s0)
                # Angle at v2: cos(theta2) = (s0^2 + s1^2 - s2^2) / (2 * s0 * s1)

                if i == 0:
                    cos_t = (s1**2 + s2**2 - s0**2) / (2 * s1 * s2)
                elif i == 1:
                    cos_t = (s2**2 + s0**2 - s1**2) / (2 * s2 * s0)
                else:
                    cos_t = (s0**2 + s1**2 - s2**2) / (2 * s0 * s1)

                angles[v_idx[i]] += math.acos(max(-1.0, min(1.0, cos_t)))

        # Curvature K_i = 2*pi - sum(angles)
        return 2 * math.pi - angles, {}

    def _get_boundary_vertices(self) -> Set[int]:
        """Identifies indices of vertices on the mesh boundary."""
        edge_counts = {}
        for face in self.mesh.faces:
            v = face.v_indices
            for i in range(3):
                e = tuple(sorted((v[i], v[(i + 1) % 3])))
                edge_counts[e] = edge_counts.get(e, 0) + 1

        boundary_v = set()
        for e, count in edge_counts.items():
            if count == 1:
                boundary_v.add(e[0])
                boundary_v.add(e[1])
        return boundary_v
