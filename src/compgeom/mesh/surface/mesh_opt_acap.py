"""ACAP optimization for mesh deformation."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Set, Tuple

import numpy as np
from numpy.typing import NDArray

from compgeom.mesh.mesh_topology import MeshTopology
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def _nearest_point_on_triangle(
    p: NDArray[np.float64], v0: NDArray[np.float64], v1: NDArray[np.float64], v2: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Find the nearest point on a triangle to a query point."""
    edge0 = v1 - v0
    edge1 = v2 - v0
    v0_to_p = p - v0

    d1 = np.dot(edge0, v0_to_p)
    d2 = np.dot(edge1, v0_to_p)

    if d1 <= 0 and d2 <= 0:
        return v0

    edge1_to_p = p - v1
    d3 = np.dot(edge0, edge1_to_p)
    d4 = np.dot(edge1, edge1_to_p)
    if d3 >= 0 and d4 <= d3:
        return v1

    edge2_to_p = p - v2
    d5 = np.dot(edge0, edge2_to_p)
    d6 = np.dot(edge1, edge2_to_p)
    if d6 >= 0 and d5 <= d6:
        return v2

    denom = np.dot(edge0, edge0) * np.dot(edge1, edge1) - np.dot(edge0, edge1) ** 2
    if abs(denom) < 1e-12:
        return v0

    v = (d1 * np.dot(edge1, edge1) - d2 * np.dot(edge0, edge1)) / denom
    w = (d2 * np.dot(edge0, edge0) - d1 * np.dot(edge0, edge1)) / denom

    if 0 <= v and 0 <= w and v + w <= 1:
        return v0 + v * edge0 + w * edge1

    proj0 = v0 + edge0 * max(0, min(1, d1 / (np.dot(edge0, edge0) + 1e-12)))
    proj1 = v0 + edge1 * max(0, min(1, d2 / (np.dot(edge1, edge1) + 1e-12)))

    d0 = np.linalg.norm(p - proj0)
    d1 = np.linalg.norm(p - proj1)
    d_orig = np.linalg.norm(p - v0)

    if d0 <= d1 and d0 <= d_orig:
        return proj0
    elif d1 <= d_orig:
        return proj1
    else:
        return v0


def project_point_to_local_mesh(
    vertex_idx: int,
    point: NDArray[np.float64],
    original_mesh: TriMesh,
    vertex_to_faces: Dict[int, list[int]],
) -> NDArray[np.float64]:
    """Project a point onto the local neighborhood of the mesh around a vertex.

    Only searches within the 1-ring faces around the vertex to preserve topological locality.
    """
    local_face_indices = vertex_to_faces.get(vertex_idx, [])

    if not local_face_indices:
        return point.copy()

    min_dist_sq = float("inf")
    nearest = point.copy()

    for face_idx in local_face_indices:
        face = original_mesh.faces[face_idx]
        v0 = np.array(
            [original_mesh.vertices[face[0]].x, original_mesh.vertices[face[0]].y, original_mesh.vertices[face[0]].z]
        )
        v1 = np.array(
            [original_mesh.vertices[face[1]].x, original_mesh.vertices[face[1]].y, original_mesh.vertices[face[1]].z]
        )
        v2 = np.array(
            [original_mesh.vertices[face[2]].x, original_mesh.vertices[face[2]].y, original_mesh.vertices[face[2]].z]
        )

        np_pt = _nearest_point_on_triangle(point, v0, v1, v2)
        dist_sq = np.sum((point - np_pt) ** 2)

        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            nearest = np_pt

    return nearest


class MeshACAP:
    """ACAP optimization for mesh deformation.

    Uses cotangent weights to preserve angles (conformal) while projecting
    vertices onto the surface of the original mesh, constrained to local neighborhood.
    """

    def __init__(
        self,
        mesh: TriMesh,
        original_mesh: TriMesh,
        fixed_indices: Set[int] | None = None,
    ) -> None:
        self.mesh = mesh
        self.original_mesh = original_mesh

        if fixed_indices is None:
            self.fixed_indices = set(mesh.faces[0]) if mesh.faces else set()
        else:
            self.fixed_indices = fixed_indices

        self.topology = MeshTopology(mesh)

        self.current_vertices = np.array([[v.x, v.y, v.z] for v in mesh.vertices], dtype=np.float64)
        self.faces = np.array(mesh.faces, dtype=np.int32)

        self._weights: Dict[Tuple[int, int], float] = {}
        self._total_weight: Dict[int, float] = {}
        self._vertex_to_faces: Dict[int, list[int]] = {}
        self._precompute_cotan_weights()
        self._build_vertex_to_faces()

    def _precompute_cotan_weights(self) -> None:
        """Precompute cotangent weights from the original mesh."""
        weights = defaultdict(float)
        total_weight = defaultdict(float)

        for face in self.original_mesh.faces:
            for i in range(3):
                idx0 = face[i]
                idx1 = face[(i + 1) % 3]
                idx2 = face[(i + 2) % 3]

                v0, v1, v2 = [self.original_mesh.vertices[idx] for idx in [idx0, idx1, idx2]]
                p0 = np.array([v0.x, v0.y, v0.z])
                p1 = np.array([v1.x, v1.y, v1.z])
                p2 = np.array([v2.x, v2.y, v2.z])

                va = p0 - p2
                vb = p1 - p2

                cross_len = np.linalg.norm(np.cross(va, vb))
                dot = np.dot(va, vb)

                cot = dot / cross_len if cross_len > 1e-12 else 0.0
                w = 0.5 * cot

                u, v = sorted((idx0, idx1))
                weights[(u, v)] += w
                total_weight[idx0] += w
                total_weight[idx1] += w

        self._weights = dict(weights)
        self._total_weight = dict(total_weight)

    def _build_vertex_to_faces(self) -> None:
        """Build vertex-to-faces adjacency for the original mesh."""
        vertex_to_faces = defaultdict(list)
        for face_idx, face in enumerate(self.original_mesh.faces):
            for vi in face:
                vertex_to_faces[vi].append(face_idx)
        self._vertex_to_faces = dict(vertex_to_faces)

    def optimize(self, iterations: int = 50, step_size: float = 0.5) -> NDArray[np.float64]:
        """Run ACAP optimization on the mesh, projecting to original mesh surface.

        Args:
            iterations: Number of optimization iterations
            step_size: Interpolation factor between current and target positions

        Returns:
            Optimized vertex positions
        """
        fixed_mask = np.zeros(len(self.current_vertices), dtype=bool)
        for idx in self.fixed_indices:
            fixed_mask[idx] = True

        for _ in range(iterations):
            new_verts = self.current_vertices.copy()
            for i in range(len(self.current_vertices)):
                if fixed_mask[i] or self._total_weight.get(i, 0) == 0:
                    continue

                neighbors = self.topology.vertex_neighbors(i)
                if not neighbors:
                    continue

                weighted_sum = np.zeros(3)
                for nb_idx in neighbors:
                    w = self._weights[tuple(sorted((i, nb_idx)))]
                    weighted_sum += w * self.current_vertices[nb_idx]

                avg_pos = weighted_sum / self._total_weight[i]
                update = (1.0 - step_size) * self.current_vertices[i] + step_size * avg_pos

                new_verts[i] = project_point_to_local_mesh(i, update, self.original_mesh, self._vertex_to_faces)

            self.current_vertices = new_verts

        return self.current_vertices


def mesh_acap_optimize(
    mesh: TriMesh,
    original_mesh: TriMesh,
    iterations: int = 50,
    step_size: float = 0.5,
) -> TriMesh:
    """Optimize a mesh using ACAP, projecting to original mesh surface.

    Args:
        mesh: The current mesh
        original_mesh: The original mesh before deformation
        iterations: Number of ACAP iterations
        step_size: Step size for optimization

    Returns:
        Optimized TriMesh
    """
    from compgeom.kernel import Point3D

    optimizer = MeshACAP(mesh, original_mesh)

    optimized = optimizer.optimize(iterations=iterations, step_size=step_size)

    vertices = [Point3D(v[0], v[1], v[2], id=i) for i, v in enumerate(optimized)]
    return TriMesh(vertices, [tuple(f) for f in mesh.faces])
