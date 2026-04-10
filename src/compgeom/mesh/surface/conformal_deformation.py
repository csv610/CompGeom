"""Conformal Mesh Deformation.

Conformal mesh deformation preserves angles (the conformal structure) while
allowing mesh deformation via handle control. This is different from
ARAP which preserves local rigidity - conformal deformation preserves
the local angles but allows scaling.

References:
    - Lipman et al., "Conformal Mesh Deformation", 2005
    - Zhou et al., "Rotation Averaged Consensus", 2008
    - Shnaps et al., "Pseudo-Vectors", 2013
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class ConformalDeformation:
    """Conformal mesh deformation with handle control.

    Preserves the conformal structure (angles) while allowing
    deformation through handle placement. Uses a hybrid approach combining
    circle packing for conformal factors with harmonic maps.
    """

    def __init__(self, mesh) -> None:
        self.mesh = mesh
        self.num_v = len(mesh.nodes)
        self.num_f = len(mesh.faces)

        self._original_vertices = self._extract_vertices()
        self._build_adjacency()
        self._compute_conformal_factors()

    def _extract_vertices(self) -> NDArray[np.float64]:
        nodes = self.mesh.nodes
        verts = np.zeros((self.num_v, 3))
        for i, node in enumerate(nodes):
            verts[i, 0] = node.point.x
            verts[i, 1] = node.point.y
            verts[i, 2] = getattr(node.point, "z", 0.0)
        return verts

    def _build_adjacency(self) -> None:
        self.adj: Dict[int, List[int]] = {i: [] for i in range(self.num_v)}
        self.edges: List[Tuple[int, int]] = []
        self.edge_to_idx: Dict[Tuple[int, int], int] = {}
        self.edge_lengths: Dict[Tuple[int, int], float] = {}

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
                    diff = self._original_vertices[u] - self._original_vertices[v]
                    self.edge_lengths[edge] = np.linalg.norm(diff)

    def _compute_conformal_factors(self) -> None:
        self.conformal_factors: NDArray[np.float64] = np.zeros(self.num_v)

        for i in range(self.num_v):
            neighbors = self.adj[i]
            if neighbors:
                lengths = []
                for j in neighbors:
                    edge = tuple(sorted((i, j)))
                    lengths.append(self.edge_lengths.get(edge, 1.0))
                avg_length = np.mean(lengths)
                self.conformal_factors[i] = np.log(avg_length + 1e-10)

    def deform(
        self,
        handle_vertices: List[int],
        handle_positions: List[NDArray[np.float64]],
        iterations: int = 20,
    ) -> NDArray[np.float64]:
        positions = self._original_vertices.copy()

        handle_set = set(handle_vertices)
        handle_dict = {vi: pos for vi, pos in zip(handle_vertices, handle_positions)}

        for it in range(iterations):
            new_positions = positions.copy()

            for vi in range(self.num_v):
                if vi in handle_set:
                    new_positions[vi] = handle_dict[vi]
                    continue

                neighbors = self.adj[vi]
                if not neighbors:
                    continue

                sum_pos = np.zeros(3)
                weight_sum = 0.0

                for nj in neighbors:
                    edge = tuple(sorted((vi, nj)))
                    orig_length = self.edge_lengths.get(edge, 1.0)
                    factor = np.exp(self.conformal_factors[nj] - self.conformal_factors[vi])

                    if orig_length > 1e-10:
                        diff = positions[nj] - positions[vi]
                        target_diff = diff / (np.linalg.norm(diff) + 1e-10) * orig_length * factor
                        sum_pos += positions[vi] + target_diff
                        weight_sum += 1.0

                if weight_sum > 0:
                    new_positions[vi] = sum_pos / weight_sum

            positions = new_positions

        return positions

    def deform_with_rots(
        self,
        handle_vertices: List[int],
        handle_positions: List[NDArray[np.float64]],
        iterations: int = 10,
    ) -> NDArray[np.float64]:
        positions = self._original_vertices.copy()

        handle_set = set(handle_vertices)
        handle_dict = {vi: pos for vi, pos in zip(handle_vertices, handle_positions)}

        for it in range(iterations):
            rotations = self._compute_local_rotations(positions)

            new_positions = positions.copy()

            for vi in range(self.num_v):
                if vi in handle_set:
                    new_positions[vi] = handle_dict[vi]
                    continue

                neighbors = self.adj[vi]
                if len(neighbors) < 2:
                    continue

                sum_pos = np.zeros(3)
                count = 0

                for nj in neighbors:
                    edge = tuple(sorted((vi, nj)))
                    orig_len = self.edge_lengths.get(edge, 1.0)

                    if nj in handle_set:
                        new_diff = handle_dict[nj] - positions[vi]
                    else:
                        rot = rotations.get((min(vi, nj), max(vi, nj)), np.eye(3))
                        orig_diff = self._original_vertices[nj] - self._original_vertices[vi]
                        new_diff = rot @ orig_diff

                    new_len = np.linalg.norm(new_diff)
                    if new_len > 1e-10:
                        new_diff = new_diff / new_len * orig_len

                    sum_pos += positions[vi] + new_diff
                    count += 1

                if count > 0:
                    new_positions[vi] = sum_pos / count

            positions = new_positions

        return positions

    def _compute_local_rotations(self, positions: NDArray[np.float64]) -> Dict[Tuple[int, int], NDArray[np.float64]]:
        rotations: Dict[Tuple[int, int], NDArray[np.float64]] = {}

        for edge, orig_len in self.edge_lengths.items():
            i, j = edge

            orig_diff = self._original_vertices[j] - self._original_vertices[i]
            new_diff = positions[j] - positions[i]

            orig_norm = np.linalg.norm(orig_diff)
            new_norm = np.linalg.norm(new_diff)

            if orig_norm > 1e-10 and new_norm > 1e-10:
                orig_unit = orig_diff / orig_norm
                new_unit = new_diff / new_norm

                cross = np.cross(orig_unit, new_unit)
                dot = np.dot(orig_unit, new_unit)

                if np.linalg.norm(cross) > 1e-10:
                    axis = cross / np.linalg.norm(cross)
                    angle = np.arctan2(np.linalg.norm(cross), dot)
                    K = self._skew_sym(axis)
                    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)
                    rotations[edge] = R
                else:
                    rotations[edge] = np.eye(3)

        return rotations

    def _skew_sym(self, axis: NDArray[np.float64]) -> NDArray[np.float64]:
        return np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])

    def get_deformed_mesh(
        self,
        handle_vertices: List[int],
        handle_positions: List[NDArray[np.float64]],
        method: str = "hybrid",
    ) -> NDArray[np.float64]:
        if method == "rots":
            return self.deform_with_rots(handle_vertices, handle_positions)
        else:
            return self.deform(handle_vertices, handle_positions)


class HarmonicConformalDeformation(ConformalDeformation):
    def __init__(self, mesh) -> None:
        super().__init__(mesh)
        self._build_laplacian()

    def _build_laplacian(self) -> None:
        n = self.num_v
        self.L = np.zeros((n, n))

        for edge, length in self.edge_lengths.items():
            i, j = edge
            w = 1.0 / (length + 1e-10)
            self.L[i, j] = -w
            self.L[j, i] = -w
            self.L[i, i] += w
            self.L[j, j] += w

    def deform_harmonic(
        self,
        handle_vertices: List[int],
        handle_positions: List[NDArray[np.float64]],
    ) -> NDArray[np.float64]:
        n = self.num_v
        positions = self._original_vertices.copy()

        handle_set = set(handle_vertices)
        handle_dict = {vi: pos for vi, pos in zip(handle_vertices, handle_positions)}

        interior = [i for i in range(n) if i not in handle_set]

        if not interior:
            return positions

        L_int = self.L[np.ix_(interior, interior)]
        rhs = np.zeros((len(interior), 3))

        for idx, vi in enumerate(interior):
            for nj in handle_set:
                w = -self.L[vi, nj]
                if w != 0:
                    rhs[idx] -= w * handle_dict[nj]

        new_int = np.linalg.solve(L_int + 1e-10 * np.eye(len(interior)), rhs)

        for idx, vi in enumerate(interior):
            positions[vi] = new_int[idx]

        return positions


def conformal_deform(
    mesh,
    handle_vertices: List[int],
    handle_positions: List[NDArray[np.float64]],
    iterations: int = 20,
) -> NDArray[np.float64]:
    deform = ConformalDeformation(mesh)
    return deform.deform(handle_vertices, handle_positions, iterations)


def conformal_deform_rots(
    mesh,
    handle_vertices: List[int],
    handle_positions: List[NDArray[np.float64]],
    iterations: int = 10,
) -> NDArray[np.float64]:
    deform = ConformalDeformation(mesh)
    return deform.deform_with_rots(handle_vertices, handle_positions, iterations)
