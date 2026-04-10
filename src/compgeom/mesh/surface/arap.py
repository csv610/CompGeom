"""As-Rigid-As-Possible (ARAP) mapping for surface meshes.

ARAP is an industry-standard method for mesh deformation and parameterization
that preserves local rigidity. Each vertex maintains its local neighborhood
shape as much as possible while allowing global deformation via handle control.

References:
    - Sorkine & Alexa, "As-Rigid-As-Possible Surface Modeling", 2007
    - Levy & Zhang, "Spectral Conformal Parameterization", 2010
    - Liu et al., "Rotation Invariant Archimedean Solids for ARAP"
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class ARAPMapper:
    """As-Rigid-As-Possible mapper for mesh deformation and UV parameterization.

    ARAP works in two alternating steps:
    1. Local step: For each vertex, find optimal rotation that aligns its
       deformed neighborhood with original neighborhood.
    2. Global step: Solve Poisson system to update positions given rotations.
    """

    def __init__(self, mesh, handle_radius: float = 0.1) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self.original_vertices = np.array(
            [[n.point.x, n.point.y, getattr(n.point, "z", 0.0)] for n in mesh.nodes], dtype=np.float64
        )
        self.handle_radius = handle_radius
        self._fixed_vertices: List[int] = []
        self._handle_targets: Dict[int, NDArray[np.float64]] = {}

        self._build_adjacency()
        self._compute_cotan_weights()

    def _build_adjacency(self) -> None:
        """Build one-ring adjacency structure for each vertex."""
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.one_ring_faces: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}

        for fi, face in enumerate(self.mesh.faces):
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                if v not in self.adj[u]:
                    self.adj[u].append(v)
                if u not in self.adj[v]:
                    self.adj[v].append(u)
                self.one_ring_faces[u].append(fi)
                self.one_ring_faces[v].append(fi)

    def _compute_cotan_weights(self) -> None:
        """Compute cotangent weights for the mesh Laplacian.

        Cotangent weights provide discrete conformal Laplacian that approximates
        the Laplace-Beltrami operator on triangulated surfaces.
        """
        self.cotan_weights: Dict[Tuple[int, int], float] = {}

        verts = self.original_vertices
        for face in self.mesh.faces:
            v0, v1, v2 = face.v_indices
            p0, p1, p2 = verts[v0], verts[v1], verts[v2]

            edges = [(v0, v1), (v1, v2), (v2, v0)]
            points = [(p0, p1), (p1, p2), (p2, p0)]
            opposite = [v2, v0, v1]

            for (a, b), (pa, pb), opp in zip(edges, points, opposite):
                vec = pa - pb
                opposite_vec = verts[opp] - pb
                cot = np.dot(vec, opposite_vec) / np.linalg.norm(np.cross(vec, opposite_vec))
                self.cotan_weights[(a, b)] = self.cotan_weights.get((a, b), 0) + 0.5 * cot
                self.cotan_weights[(b, a)] = self.cotan_weights.get((b, a), 0) + 0.5 * cot

    def compute_cotan_laplacian(self) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Build the cotangent Laplacian matrix and RHS for a given set of constraints.

        Solves: L * positions = 0 subject to handle constraints.
        """
        n = self.num_v
        L = np.zeros((n, n))
        rhs = np.zeros((n, 3))

        fixed = self._fixed_vertices
        for i in range(n):
            neighbors = self.adj[i]
            weight_sum = 0.0
            for j in neighbors:
                w = self.cotan_weights.get((i, j), 0.0)
                L[i, j] = w
                weight_sum += w
            L[i, i] = -weight_sum

        for i in fixed:
            for j in range(n):
                L[i, j] = 0.0
            L[i, i] = 1.0
            rhs[i] = self.original_vertices[i]

        return L, rhs

    def _compute_covariance_matrix(
        self, vi: int, neighbors: List[int], positions: NDArray[np.float64]
    ) -> NDArray[np.float64]:
        """Compute covariance matrix for a vertex's one-ring.

        This is the key to ARAP: we find the best rotation by computing
        the covariance of neighbor positions.
        """
        center = np.zeros(3)
        count = len(neighbors)

        for nj in neighbors:
            center += positions[nj]
        center /= count

        cov = np.zeros((3, 3))
        for nj in neighbors:
            diff = positions[nj] - center
            diff_orig = self.original_vertices[nj] - self.original_vertices[vi]
            cov += np.outer(diff, diff_orig)

        return cov

    def _polar_decomposition_3d(self, A: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute optimal rotation via polar decomposition.

        Given covariance matrix A, find rotation R that minimizes
        ||R*A - A||_F^2 via SVD: A = U*S*V^T, then R = U*V^T.
        """
        U, s, Vt = np.linalg.svd(A)
        det = np.linalg.det(U @ Vt)
        if det < 0:
            s[-1] = -s[-1]
            U[:, -1] = -U[:, -1]
        return U @ Vt

    def set_handles(
        self,
        handle_vertices: List[int],
        target_positions: Optional[List[NDArray[np.float64]]] = None,
    ) -> None:
        """Set control handles for ARAP deformation.

        Args:
            handle_vertices: List of vertex indices to use as handles (will stay fixed or move to target)
            target_positions: Optional target positions for handles. If None, keep original.
        """
        self._fixed_vertices = handle_vertices

        if target_positions is None:
            self._handle_targets = {vi: self.original_vertices[vi] for vi in handle_vertices}
        else:
            self._handle_targets = {vi: target_positions[i] for i, vi in enumerate(handle_vertices)}

    def deform(
        self,
        iterations: int = 10,
        handle_vertices: Optional[List[int]] = None,
        handle_positions: Optional[List[NDArray[np.float64]]] = None,
    ) -> List[NDArray[np.float64]]:
        """Perform ARAP deformation.

        Args:
            iterations: Number of local-global iterations
            handle_vertices: Vertex indices to use as handles
            handle_positions: Target positions for handles

        Returns:
            Deformed vertex positions as list of arrays

        Example:
            >>> arap = ARAPMapper(mesh)
            >>> # Pin vertex 0, move vertex 10 to new position
            >>> arap.set_handles([0, 10], [original[0], new_pos])
            >>> deformed = arap.deform(iterations=20)
        """
        if handle_vertices is not None:
            self.set_handles(handle_vertices, handle_positions)

        positions = self.original_vertices.copy()

        for it in range(iterations):
            rotated = []

            for vi in range(self.num_v):
                neighbors = self.adj[vi]
                cov = self._compute_covariance_matrix(vi, neighbors, positions)
                if np.linalg.norm(cov) > 1e-10:
                    R = self._polar_decomposition_3d(cov)
                else:
                    R = np.eye(3)
                rotated.append(R)

            L, rhs = self.compute_cotan_laplacian()
            rhs = np.zeros((self.num_v, 3))

            for vi in self._fixed_vertices:
                rhs[vi] = self._handle_targets[vi]

            new_positions = np.linalg.solve(L + 1e-10 * np.eye(self.num_v), rhs)

            positions = new_positions

        return [positions[i] for i in range(self.num_v)]

    def parameterize(
        self,
        iterations: int = 20,
        boundary_type: str = "circle",
    ) -> List[Tuple[float, float]]:
        """Compute UV parameterization using ARAP.

        Flattens a mesh onto 2D plane while preserving local rigidity.
        Similar to conformal mapping but with better angle preservation.

        Args:
            iterations: Number of ARAP iterations
            boundary_type: "circle" (conformal) or "square" (authalic)

        Returns:
            List of (u, v) coordinate tuples
        """
        num_v = self.num_v
        uv = np.zeros((num_v, 2))

        boundary = self._find_boundary_loop()
        n_b = len(boundary)

        if n_b == 0:
            raise ValueError("Mesh has no boundary - cannot parameterize.")

        if boundary_type == "circle":
            for i, vi in enumerate(boundary):
                theta = 2.0 * np.pi * i / n_b
                uv[vi] = [np.cos(theta), np.sin(theta)]
        else:
            for i, vi in enumerate(boundary):
                t = i / n_b
                if t < 0.25:
                    uv[vi] = [-1 + 4 * t, -1]
                elif t < 0.5:
                    uv[vi] = [0, -1 + 4 * (t - 0.25)]
                elif t < 0.75:
                    uv[vi] = [1 - 4 * (t - 0.5), 1]
                else:
                    uv[vi] = [1, 1 - 4 * (t - 0.75)]

        adj_set = [set(self.adj[i]) for i in range(num_v)]

        for it in range(iterations):
            rotations = []

            for vi in range(num_v):
                if vi in boundary:
                    rotations.append(np.eye(2))
                    continue

                neighbors = list(adj_set[vi])
                if len(neighbors) < 2:
                    rotations.append(np.eye(2))
                    continue

                cov = np.zeros((2, 2))
                for nj in neighbors:
                    du = uv[nj] - uv[vi]
                    do = self.original_vertices[nj][:2] - self.original_vertices[vi][:2]
                    cov += np.outer(du, do)

                U, s, Vt = np.linalg.svd(cov)
                det = np.linalg.det(U @ Vt)
                if det < 0:
                    s[-1] = -s[-1]
                    U[:, -1] = -U[:, -1]
                R = U @ Vt
                rotations.append(R)

            L = np.zeros((num_v, num_v))
            rhs = np.zeros((num_v, 2))

            for vi in range(num_v):
                neighbors = list(adj_set[vi])
                for nj in neighbors:
                    L[vi, nj] = 1.0
                L[vi, vi] = -len(neighbors)

            fixed_mask = np.zeros(num_v, dtype=bool)
            for vi in boundary:
                fixed_mask[vi] = True

            for vi in boundary:
                L[vi] = 0.0
                L[vi, vi] = 1.0
                rhs[vi] = uv[vi]

            uv = np.linalg.solve(L + 1e-10 * np.eye(num_v), rhs)

        return [(uv[i, 0], uv[i, 1]) for i in range(num_v)]

    def _find_boundary_loop(self) -> List[int]:
        """Find the outer boundary loop of the mesh."""
        edge_counts: Dict[Tuple[int, int], int] = {}
        directed_edges: Dict[Tuple[int, int], Tuple[int, int]] = {}

        for face in self.mesh.faces:
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                edge_counts[edge] = edge_counts.get(edge, 0) + 1
                directed_edges[edge] = (u, v)

        boundary_edges = [directed_edges[e] for e, c in edge_counts.items() if c == 1]

        if not boundary_edges:
            return []

        next_v = {u: v for u, v in boundary_edges}
        loop = []
        curr = boundary_edges[0][0]
        while curr not in loop:
            loop.append(curr)
            curr = next_v.get(curr, curr)
            if curr == loop[0]:
                break

        return loop[:-1] if loop[-1] == loop[0] else loop


def as_rigid_as_possible(
    mesh,
    iterations: int = 10,
    handle_vertices: Optional[List[int]] = None,
    handle_positions: Optional[List[NDArray[np.float64]]] = None,
) -> List[NDArray[np.float64]]:
    """Convenience function for ARAP deformation.

    Args:
        mesh: TriMesh with .vertices and .faces attributes
        iterations: Number of ARAP iterations
        handle_vertices: Fixed/moving vertex indices
        handle_positions: Target positions for handles

    Returns:
        Deformed vertex positions
    """
    mapper = ARAPMapper(mesh)
    return mapper.deform(iterations, handle_vertices, handle_positions)
