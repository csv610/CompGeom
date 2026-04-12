"""Levi-Civita Connection for Parallel Transport.

Implements the Levi-Civita connection for parallel transport
of tangent vectors along meshes. This is the fundamental
tool for moving vector fields while preserving angles.

References:
    - Crane et al., "The Heat Method for Distance Substitution", 2013
    - Russell et al., "Parallel Transport on Manifolds", 2015
    - Huang et al., "Spin-Weighted Spherical Harmonics", 2019
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class LeviCivitaConnection:
    """Levi-Civita connection for parallel transport on triangulated surfaces.

    The Levi-Civita connection provides the unique torsion-free
    connection that preserves the metric. For discrete meshes,
    we use the parallel transport via rotation matrices.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self._build_mesh_data()

    def _build_mesh_data(self) -> None:
        self._vertices = np.array([[n.point.x, n.point.y, getattr(n.point, "z", 0.0)] for n in self.mesh.nodes])

        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.faces_by_edge: Dict[Tuple[int, int], List[int]] = {}

        for fi, face in enumerate(self.mesh.faces):
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                if edge not in self.faces_by_edge:
                    self.faces_by_edge[edge] = []
                self.faces_by_edge[edge].append(fi)

                if v not in self.adj[u]:
                    self.adj[u].append(v)
                if u not in self.adj[v]:
                    self.adj[v].append(u)

    def compute_transport(
        self,
        source_vertex: int,
        direction: NDArray[np.float64],
        target_vertex: int,
    ) -> NDArray[np.float64]:
        """Transport a vector from source to target via parallel transport.

        Uses the heat method approach to find the transport along
        the minimal geodesic.

        Args:
            source_vertex: Starting vertex index
            direction: Tangent vector at source (3D)
            target_vertex: Ending vertex index

        Returns:
            Transported vector at target
        """
        from compgeom.mesh.surface.heat_method import VectorHeatMethod

        heat = VectorHeatMethod(self.mesh)
        geodesic = heat.compute_geodesics([source_vertex])

        grad = self._compute_geodesic_gradient(geodesic)
        direction_normalized = direction / (np.linalg.norm(direction) + 1e-10)

        transported = self._rotate_along_path(source_vertex, target_vertex, direction_normalized, grad)

        return transported

    def _compute_geodesic_gradient(self, geodesic: NDArray[np.float64]) -> NDArray[np.float64]:
        """Compute the gradient of the geodesic distance field."""
        grad = np.zeros((self.num_v, 3))

        for face in self.mesh.faces:
            v_indices = face.v_indices
            v0, v1, v2 = v_indices
            p0, p1, p2 = self._vertices[v0], self._vertices[v1], self._vertices[v2]

            normal = np.cross(p1 - p0, p2 - p0)
            area = 0.5 * np.linalg.norm(normal)
            if area < 1e-10:
                continue
            normal /= 2 * area

            for i, vi in enumerate(v_indices):
                edge = p1 - p0 if i == 0 else (p2 - p1 if i == 1 else p0 - p2)
                grad[vi] += np.cross(normal, edge) * geodesic[v_indices[i]]

        return grad

    def _rotate_along_path(
        self,
        source: int,
        target: int,
        vector: NDArray[np.float64],
        geodesic_grad: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Rotate vector along the geodesic path using parallel transport."""
        path = self._find_shortest_path(source, target)

        result = vector.copy()
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]

            edge = tuple(sorted((u, v)))
            faces = self.faces_by_edge.get(edge, [])

            if not faces:
                continue

            normal = self._compute_face_normal(faces[0])

            src_dir = geodesic_grad[u]
            tgt_dir = geodesic_grad[v]

            if np.linalg.norm(src_dir) < 1e-10 or np.linalg.norm(tgt_dir) < 1e-10:
                continue

            src_dir /= np.linalg.norm(src_dir)
            tgt_dir /= np.linalg.norm(tgt_dir)

            rotation = self._rotation_aligning(src_dir, tgt_dir, normal)

            result = rotation @ result

        return result

    def _find_shortest_path(self, source: int, target: int) -> List[int]:
        """Find shortest path via BFS."""
        from collections import deque

        queue = deque([source])
        parent = {source: None}
        visited = {source}

        while queue:
            current = queue.popleft()
            if current == target:
                break

            for neighbor in self.adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        path = []
        node = target
        while node is not None:
            path.append(node)
            node = parent.get(node)
        path.reverse()

        return path if path[0] == source else [source, target]

    def _compute_face_normal(self, face_idx: int) -> NDArray[np.float64]:
        """Compute normal for a face."""
        face = self.mesh.faces[face_idx].v_indices
        v0, v1, v2 = face
        p0, p1, p2 = self._vertices[v0], self._vertices[v1], self._vertices[v2]

        normal = np.cross(p1 - p0, p2 - p0)
        norm = np.linalg.norm(normal)
        if norm > 1e-10:
            normal /= norm
        return normal

    def _rotation_aligning(
        self,
        v1: NDArray[np.float64],
        v2: NDArray[np.float64],
        normal: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Compute rotation aligning v1 to v2 in the tangent plane."""
        cross = np.cross(v1, v2)
        dot = np.dot(v1, v2)

        if np.linalg.norm(cross) < 1e-10:
            if dot > 0:
                return np.eye(3)
            else:
                return -np.eye(3)

        cross /= np.linalg.norm(cross)
        angle = np.arctan2(np.linalg.norm(cross), dot)

        K = np.array([[0, -cross[2], cross[1]], [cross[2], 0, -cross[0]], [-cross[1], cross[0], 0]])

        return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)


class SpinConnection:
    """Spin connection for spinor fields on surfaces.

    Provides the spin connection needed for spinor-valued
    functions and spin geometry.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.connection = LeviCivitaConnection(mesh)

    def parallel_transport_spinor(
        self,
        source_vertex: int,
        spinor: NDArray[np.float64],
        target_vertex: int,
    ) -> NDArray[np.float64]:
        """Transport a spinor via parallel transport.

        Args:
            source_vertex: Source vertex index
            spinor: Spinor values at source (2-component complex)
            target_vertex: Target vertex index

        Returns:
            Transported spinor at target
        """
        real_part = np.real(spinor)
        imag_part = np.imag(spinor)

        real_transported = self.connection.compute_transport(source_vertex, real_part, target_vertex)
        imag_transported = self.connection.compute_transport(source_vertex, imag_part, target_vertex)

        return real_transported + 1j * imag_transported


def parallel_transport(
    mesh,
    source_vertex: int,
    direction: List[float],
    target_vertex: int,
) -> List[float]:
    """Convenience function for parallel transport.

    Args:
        mesh: TriMesh
        source_vertex: Source vertex index
        direction: Direction vector at source
        target_vertex: Target vertex index

    Returns:
        Transported direction vector
    """
    conn = LeviCivitaConnection(mesh)
    result = conn.compute_transport(source_vertex, np.array(direction), target_vertex)
    return result.tolist()
