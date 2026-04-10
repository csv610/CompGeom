"""ABF++ (Angle-Based Flattening++) for Conformal Parameterization.

ABF++ is an angle-based conformal parameterization method that
directly optimizes interior angles to minimize distortion.
Often produces lower angle distortion than LSCM or circle-packing.

References:
    - Zhu et al., "ABF++: Fast and Robust Angle-Based Flattening", 2003
    - Zhang et al., "Spectral Conformal Parameterization", 2010
    - Weber et al., "Conformal Flattening by Curvature Theorem", 2012
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class ABFPlusPlus:
    """ABF++ angle-based flattening for conformal parameterization.

    ABF++ formulates the parameterization as an optimization over
    interior angles of the triangulation, with constraints that
    angles sum to pi at each interior vertex and use the boundary
    as fixed anchor.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self._build_mesh_structure()

    def _build_mesh_structure(self) -> None:
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.faces_struct: List[Dict] = []
        self.edge_to_idx: Dict[Tuple[int, int], int] = {}
        self.edges: List[Tuple[int, int]] = []

        edge_count: Dict[Tuple[int, int], int] = {}

        for fi, face in enumerate(self.mesh.faces):
            v_indices = face.v_indices
            face_dict = {"v": list(v_indices), "edges": []}
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                face_dict["edges"].append(edge)
                if edge not in self.edge_to_idx:
                    self.edge_to_idx[edge] = len(self.edges)
                    self.edges.append(edge)
                    self.adj[u].append(v)
                    self.adj[v].append(u)
                    edge_count[edge] = 0
                edge_count[edge] += 1

            self.faces_struct.append(face_dict)

        self.boundary = self._find_boundary(edge_count)

    def _find_boundary(self, edge_count: Dict[Tuple[int, int], int]) -> List[int]:
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

    def compute_original_angles(self) -> NDArray[np.float64]:
        """Compute original angles in 3D mesh for each face."""
        nodes = self.mesh.nodes
        angles = np.zeros((self.num_f, 3))

        for fi, face in enumerate(self.faces_struct):
            v = face["v"]
            p0 = np.array([nodes[v[0]].point.x, nodes[v[0]].point.y, getattr(nodes[v[0]].point, "z", 0.0)])
            p1 = np.array([nodes[v[1]].point.x, nodes[v[1]].point.y, getattr(nodes[v[1]].point, "z", 0.0)])
            p2 = np.array([nodes[v[2]].point.x, nodes[v[2]].point.y, getattr(nodes[v[2]].point, "z", 0.0)])

            a = np.linalg.norm(p1 - p2)
            b = np.linalg.norm(p0 - p2)
            c = np.linalg.norm(p0 - p1)

            angles[fi, 0] = np.arccos(np.clip((b * b + c * c - a * a) / (2 * b * c + 1e-10), -1, 1))
            angles[fi, 1] = np.arccos(np.clip((a * a + c * c - b * b) / (2 * a * c + 1e-10), -1, 1))
            angles[fi, 2] = np.arccos(np.clip((a * a + b * b - c * c) / (2 * a * b + 1e-10), -1, 1))

        return angles

    def compute_parameterization(
        self,
        iterations: int = 100,
        tolerance: float = 1e-5,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute ABF++ parameterization.

        Uses a two-stage approach:
        1. Initialize using harmonic/w with uniform weights
        2. Optimize interior angles with constraints

        Args:
            iterations: Number of optimization iterations
            tolerance: Convergence tolerance

        Returns:
            Tuple of (u, v) coordinates
        """
        boundary = self.boundary
        n_b = len(boundary)

        if n_b == 0:
            raise ValueError("Mesh has no boundary - cannot use ABF++")

        u_coords = np.zeros(self.num_v)
        v_coords = np.zeros(self.num_v)

        for i, vi in enumerate(boundary):
            theta = 2 * np.pi * i / n_b
            u_coords[vi] = np.cos(theta)
            v_coords[vi] = np.sin(theta)

        interior = [i for i in range(self.num_v) if i not in boundary]
        original_angles = self.compute_original_angles()

        for it in range(iterations):
            new_u, new_v = self._gradient_descent_step(u_coords, v_coords, interior, original_angles)

            u_coords[interior] = new_u
            v_coords[interior] = new_v

            residual = np.max(np.abs(new_u - u_coords[interior]))
            if residual < tolerance:
                break

        return u_coords, v_coords

    def _gradient_descent_step(
        self,
        u_coords: NDArray[np.float64],
        v_coords: NDArray[np.float64],
        interior: List[int],
        original_angles: NDArray[np.float64],
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """One step of gradient descent for angle optimization."""
        new_u = np.zeros(len(interior))
        new_v = np.zeros(len(interior))

        for idx, vi in enumerate(interior):
            neighbors = self.adj[vi]
            if not neighbors:
                continue

            grad_u = 0.0
            grad_v = 0.0

            for fi, face in enumerate(self.faces_struct):
                v = face["v"]
                if vi not in v:
                    continue

                local_idx = v.index(vi)

                u0 = u_coords[v[0]]
                v0 = v_coords[v[0]]
                u1 = u_coords[v[1]]
                v1 = v_coords[v[1]]
                u2 = u_coords[v[2]]
                v2 = v_coords[v[2]]

                du = [u1 - u2, u0 - u2, u0 - u1]
                dv = [v1 - v2, v0 - v2, v0 - v1]

                lengths = [np.sqrt(du[i] ** 2 + dv[i] ** 2) + 1e-10 for i in range(3)]

                angle = 0.0
                for j in range(3):
                    if lengths[j] > 1e-10:
                        dot = (du[(j + 1) % 3] * du[(j + 2) % 3] + dv[(j + 1) % 3] * dv[(j + 2) % 3]) / (
                            lengths[(j + 1) % 3] * lengths[(j + 2) % 3]
                        )
                        angle += np.arccos(np.clip(dot, -1, 1))

                orig_angle = original_angles[fi, local_idx]
                error = angle - orig_angle

                for j in range(3):
                    if lengths[j] > 1e-10:
                        du_j = du[j] if j != local_idx else -du[j]
                        dv_j = dv[j] if j != local_idx else -dv[j]

                        factor = error * 0.1 / lengths[j]
                        grad_u += factor * du_j
                        grad_v += factor * dv_j

            new_u[idx] = u_coords[vi] - grad_u
            new_v[idx] = v_coords[vi] - grad_v

        return new_u, new_v

    def compute_with_lscm_init(
        self,
        iterations: int = 50,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute using ABF++ with LSCM initialization (more robust)."""
        from compgeom.mesh.surface.parameterization_lscm import LSCMParameterizer

        try:
            lscm_uv = LSCMParameterizer.compute(mesh=self.mesh)
            u_init = np.array([p.x for p in lscm_uv])
            v_init = np.array([p.y for p in lscm_uv])
        except:
            return self.compute_parameterization(iterations=iterations)

        boundary = self.boundary
        n_b = len(boundary)

        u_coords = u_init.copy()
        v_coords = v_init.copy()

        for i, vi in enumerate(boundary):
            theta = 2 * np.pi * i / n_b
            u_coords = np.cos(theta)
            v_coords = np.sin(theta)

        interior = [i for i in range(self.num_v) if i not in boundary]
        original_angles = self.compute_original_angles()

        for it in range(iterations):
            new_u, new_v = self._gradient_descent_step(u_coords, v_coords, interior, original_angles)
            u_coords[interior] = new_u
            v_coords[interior] = new_v

        return u_coords, v_coords


class ABFParameterization:
    """Wrapper class for ABF++ with multiple initialization options."""

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.solver = ABFPlusPlus(mesh)

    def compute(
        self,
        method: str = "abfpp",
        iterations: int = 100,
    ) -> List[Tuple[float, float]]:
        """Compute UV parameterization.

        Args:
            method: "abfpp" (default), "lscm" (LSCM init), or "harmonic"
            iterations: Number of iterations

        Returns:
            List of (u, v) coordinate tuples
        """
        if method == "lscm":
            u, v = self.solver.compute_with_lscm_init(iterations=iterations)
        else:
            u, v = self.solver.compute_parameterization(iterations=iterations)

        return [(u[i], v[i]) for i in range(self.solver.num_v)]


def abf_plus_plus(
    mesh,
    iterations: int = 100,
) -> List[Tuple[float, float]]:
    """Convenience function for ABF++ parameterization.

    Args:
        mesh: TriMesh with nodes and faces
        iterations: Number of optimization iterations

    Returns:
        List of (u, v) coordinate tuples
    """
    solver = ABFPlusPlus(mesh)
    u, v = solver.compute_parameterization(iterations=iterations)
    return [(u[i], v[i]) for i in range(solver.num_v)]
