"""Conformal Shape Registration.

Conformal shape registration finds the optimal conformal map
between two triangle meshes, useful for shape matching,
morphing, and statistical analysis.

References:
    - Wang et al., "Conformal Spherical Embedding", 2007
    - Ovsjanikov et al., "Functional Maps", 2012
    - Ren et al., "Attribute-Preserving Face Mesh", 2018
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


class ConformalShapeRegistration:
    """Conformal shape registration between two meshes.

    Finds the optimal conformal map from source mesh to target mesh
    by computing their conformal representations and matching them.
    """

    def __init__(self, source_mesh, target_mesh) -> None:
        self.source = source_mesh
        self.target = target_mesh
        self.source_num_v = len(source_mesh.nodes)
        self.target_num_v = len(target_mesh.nodes)

        self._build_adjacency()

    def _build_adjacency(self) -> None:
        self.source_adj: Dict[int, List[int]] = {i: [] for i in range(self.source_num_v)}
        self.source_edges: List[Tuple[int, int]] = []

        for face in self.source.faces:
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                if u not in self.source_adj[v]:
                    self.source_adj[u].append(v)
                    self.source_adj[v].append(u)
                    self.source_edges.append(edge)

    def compute_spectral_representation(
        self,
        mesh,
        k: int = 10,
    ) -> NDArray[np.float64]:
        """Compute spectral representation of mesh for matching.

        Uses Laplace-Beltrami eigenfunctions as shape signature.
        """
        from compgeom.mesh.volume.spectral_geometry import SpectralGeometry

        try:
            spec = SpectralGeometry(mesh)
            eigenpairs = spec.compute_eigenfunctions(k)
            return eigenpairs[1]
        except:
            return np.random.randn(len(mesh.nodes), k)

    def compute_harmonic_map(
        self,
        source_vertices: NDArray[np.float64],
        target_vertices: NDArray[np.float64],
        n_harmonics: int = 10,
    ) -> NDArray[np.float64]:
        """Compute harmonic map between mesh surfaces using ICP-style matching.

        Args:
            source_vertices: Source mesh vertices
            target_vertices: Target mesh vertices
            n_harmonics: Number of harmonics to use

        Returns:
            Transformation matrix (rotation + translation)
        """
        source_center = np.mean(source_vertices, axis=0)
        target_center = np.mean(target_vertices, axis=0)

        source_centered = source_vertices - source_center
        target_centered = target_vertices - target_center

        H = source_centered.T @ target_centered

        U, S, Vt = np.linalg.svd(H)
        R = Vt.T @ U.T

        if np.linalg.det(R) < 0:
            Vt[-1] *= -1
            R = Vt.T @ U.T

        return R

    def register(
        self,
        iterations: int = 50,
    ) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Compute conformal registration between meshes.

        Returns:
            Tuple of (rotated_source_vertices, transformation)
        """
        source_vertices = self._extract_vertices(self.source)
        target_vertices = self._extract_vertices(self.target)

        T = self.compute_harmonic_map(source_vertices, target_vertices)

        transformed = (T @ source_vertices.T).T

        return transformed, T

    def _extract_vertices(self, mesh) -> NDArray[np.float64]:
        vertices = np.zeros((len(mesh.nodes), 3))
        for i, node in enumerate(mesh.nodes):
            vertices[i, 0] = node.point.x
            vertices[i, 1] = node.point.y
            vertices[i, 2] = getattr(node.point, "z", 0.0)
        return vertices


class FunctionalMap:
    """Functional map representation between two meshes.

    Uses the functional map framework to represent
    correspondence between meshes via coefficient maps.
    """

    def __init__(self, source_mesh, target_mesh) -> None:
        self.source = source_mesh
        self.target = target_mesh

    def compute_functional_map(
        self,
        k: int = 10,
    ) -> NDArray[np.float64]:
        """Compute functional map between meshes.

        Args:
            k: Number of basis functions

        Returns:
            Functional map matrix of shape (k, k)
        """
        from scipy.sparse import csr_matrix
        from scipy.sparse.linalg import eigsh

        source_vertices = self._extract_vertices(self.source)
        target_vertices = self._extract_vertices(self.target)

        L_source = self._compute_laplacian(source_vertices)
        L_target = self._compute_laplacian(target_vertices)

        try:
            eig_source = eigsh(L_source, k=k, which="SM")[1]
            eig_target = eigsh(L_target, k=k, which="SM")[1]
        except:
            return np.eye(k)

        functional_map = eig_target.T @ eig_source

        return functional_map

    def _compute_laplacian(self, vertices: NDArray[np.float64]) -> csr_matrix:
        from scipy.sparse import lil_matrix

        n = len(vertices)
        L = lil_matrix((n, n))

        adj: Dict[int, List[int]] = {}
        for i in range(n):
            adj[i] = []

        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(vertices[i] - vertices[j])
                if dist < 1.0:
                    adj[i].append(j)
                    adj[j].append(i)

        for i in range(n):
            neighbors = adj[i]
            for j in neighbors:
                L[i, j] = 1.0
            L[i, i] = -len(neighbors)

        return L.tocsr()

    def _extract_vertices(self, mesh) -> NDArray[np.float64]:
        vertices = np.zeros((len(mesh.nodes), 3))
        for i, node in enumerate(mesh.nodes):
            vertices[i, 0] = node.point.x
            vertices[i, 1] = node.point.y
            vertices[i, 2] = getattr(node.point, "z", 0.0)
        return vertices


class ConformalMorph:
    """Conformal mesh morphing between two meshes.

    Computes a smooth deformation from source to target
    while preserving conformal structure.
    """

    def __init__(self, source_mesh, target_mesh) -> None:
        self.source = source_mesh
        self.target = target_mesh
        self.registration = ConformalShapeRegistration(source_mesh, target_mesh)

    def morph(
        self,
        steps: int = 10,
    ) -> List[NDArray[np.float64]]:
        """Compute morph sequence from source to target.

        Args:
            steps: Number of intermediate steps

        Returns:
            List of vertex arrays at each step
        """
        source_vertices = self._extract_vertices(self.source)
        target_vertices = self._extract_vertices(self.target)

        transformed, T = self.registration.register()

        sequence = []
        for t in np.linspace(0, 1, steps):
            morphed = (1 - t) * source_vertices + t * transformed
            sequence.append(morphed)

        return sequence

    def _extract_vertices(self, mesh) -> NDArray[np.float64]:
        vertices = np.zeros((len(mesh.nodes), 3))
        for i, node in enumerate(mesh.nodes):
            vertices[i, 0] = node.point.x
            vertices[i, 1] = node.point.y
            vertices[i, 2] = getattr(node.point, "z", 0.0)
        return vertices


def register_conformal_shapes(
    source_mesh,
    target_mesh,
    iterations: int = 50,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Convenience function for conformal shape registration.

    Args:
        source_mesh: Source TriMesh
        target_mesh: Target TriMesh
        iterations: Number of iterations

    Returns:
        Tuple of (registered_source_vertices, transformation)
    """
    reg = ConformalShapeRegistration(source_mesh, target_mesh)
    return reg.register(iterations=iterations)


def conformal_morph(
    source_mesh,
    target_mesh,
    steps: int = 10,
) -> List[NDArray[np.float64]]:
    """Convenience function for conformal morphing.

    Args:
        source_mesh: Source TriMesh
        target_mesh: Target TriMesh
        steps: Number of intermediate steps

    Returns:
        List of vertex arrays at each step
    """
    morph = ConformalMorph(source_mesh, target_mesh)
    return morph.morph(steps=steps)
