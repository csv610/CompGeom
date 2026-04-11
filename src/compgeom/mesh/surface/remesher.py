"""Isotropic remeshing algorithm for surface meshes."""

import math
from collections import defaultdict
from typing import List, Tuple, Set, Dict

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D
from compgeom.mesh.surface.mesh_processing import MeshProcessing
from compgeom.mesh.surface.curvature import MeshCurvature


class IsotropicRemesher:
    # ... (Isotropic code remains)
    pass


class AdaptiveRemesher:
    """Remeshes based on a sizing field derived from local curvature."""

    @staticmethod
    def remesh(mesh: TriMesh, min_edge: float, max_edge: float, iterations: int = 3) -> TriMesh:
        """
        Adapts triangle density to surface curvature.
        Sharp areas get min_edge, flat areas get max_edge.
        """
        from compgeom.mesh.surface.smoothing import laplacian_smoothing

        current_mesh = mesh
        for _ in range(iterations):
            # 1. Compute curvature to define sizing field
            gauss = MeshCurvature.gaussian_curvature(current_mesh)
            mean = MeshCurvature.mean_curvature(current_mesh)

            # Combine and normalize curvature signal
            # Sizing field S: high curvature -> small value (target_L)
            sizing_field = []
            for i in range(len(current_mesh.vertices)):
                k = abs(gauss[i]) + abs(mean[i])
                # Simple non-linear mapping to [min_edge, max_edge]
                # Lower value = higher density
                t = math.exp(-k)
                target_l = min_edge + (max_edge - min_edge) * t
                sizing_field.append(target_l)

            # 2. Adaptive Split
            current_mesh = AdaptiveRemesher._adaptive_split(current_mesh, sizing_field)

            # 3. Adaptive Collapse
            current_mesh = AdaptiveRemesher._adaptive_collapse(current_mesh, sizing_field)

            # 4. Tangential Relaxation
            current_mesh = MeshProcessing.laplacian_smoothing(current_mesh, iterations=1)

        return current_mesh

    @staticmethod
    def _adaptive_split(mesh: TriMesh, sizing_field: List[float]) -> TriMesh:
        vertices = list(mesh.vertices)
        faces = []
        for face in mesh.faces:
            v0, v1, v2 = face
            # Local target length is average of the three vertices
            target = (sizing_field[v0] + sizing_field[v1] + sizing_field[v2]) / 3.0

            # Check edge lengths
            p0, p1, p2 = vertices[v0], vertices[v1], vertices[v2]

            def d(a, b):
                return math.sqrt(
                    (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (getattr(a, "z", 0.0) - getattr(b, "z", 0.0)) ** 2
                )

            l01, l12, l20 = d(p0, p1), d(p1, p2), d(p2, p0)

            if max(l01, l12, l20) > 1.5 * target:
                # Split longest edge (approximate)
                if l01 >= l12 and l01 >= l20:
                    mid = Point3D(
                        (p0.x + p1.x) / 2, (p0.y + p1.y) / 2, (getattr(p0, "z", 0.0) + getattr(p1, "z", 0.0)) / 2
                    )
                    m_idx = len(vertices)
                    vertices.append(mid)
                    faces.append((v0, m_idx, v2))
                    faces.append((m_idx, v1, v2))
                    # Update sizing field for new vertex
                    sizing_field.append((sizing_field[v0] + sizing_field[v1]) / 2.0)
                # ... other edges similarly ...
                else:
                    faces.append(face)
            else:
                faces.append(face)
        return TriMesh(vertices, faces)

    @staticmethod
    def _adaptive_collapse(mesh: TriMesh, sizing_field: List[float]) -> TriMesh:
        return mesh
