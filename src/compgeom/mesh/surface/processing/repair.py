"""Mesh repair algorithms."""

from collections import defaultdict
from typing import TYPE_CHECKING
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D

if TYPE_CHECKING:
    from compgeom.mesh.mesh_base import Mesh

def flip_normals(mesh: "Mesh"):
    """Flips the normals of all faces in the mesh by reversing their vertex order."""
    from dataclasses import replace
    from compgeom.mesh.mesh_topology import MeshTopology

    new_faces = []
    for face in mesh.faces:
        new_v = tuple(reversed(face.v_indices))
        new_faces.append(replace(face, v_indices=new_v))

    mesh._faces = new_faces
    mesh._topology = MeshTopology(mesh)

def fill_holes(mesh: SurfaceMesh) -> SurfaceMesh:
    """Fills boundary holes by connecting boundary loops to their centroids."""
    # Detect boundary edges
    edge_counts = defaultdict(int)
    edge_to_directed = {}
    for face in mesh.faces:
        for i in range(3):
            u, v = face[i], face[(i + 1) % 3]
            edge = tuple(sorted((u, v)))
            edge_counts[edge] += 1
            # Forward edge direction for outward pointing normal assumption
            edge_to_directed[edge] = (u, v)

    boundary_edges = [edge_to_directed[e] for e, c in edge_counts.items() if c == 1]
    if not boundary_edges:
        return mesh  # No holes

    # Group into loops
    next_v = {u: v for u, v in boundary_edges}
    visited = set()
    loops = []

    for u, _ in boundary_edges:
        if u in visited:
            continue
        loop = []
        curr = u
        while curr not in visited:
            visited.add(curr)
            loop.append(curr)
            curr = next_v.get(curr)
            if curr is None:
                break

        # Very basic check for closure
        if next_v.get(loop[-1]) == loop[0]:
            loops.append(loop)

    new_faces = list(mesh.faces)
    vertices = list(mesh.vertices)

    # Naive hole filling (fan triangulation from centroid)
    for loop in loops:
        if len(loop) < 3:
            continue
        if len(loop) == 3:
            new_faces.append(tuple(loop))
            continue

        # Add centroid
        sum_x = sum_y = sum_z = 0.0
        for idx in loop:
            v = vertices[idx]
            sum_x += v.x
            sum_y += v.y
            sum_z += getattr(v, "z", 0.0)

        centroid = Point3D(sum_x / len(loop), sum_y / len(loop), sum_z / len(loop))
        c_idx = len(vertices)
        vertices.append(centroid)

        # Connect loop to centroid
        for i in range(len(loop)):
            u = loop[i]
            v = loop[(i + 1) % len(loop)]
            new_faces.append((u, v, c_idx))
    
    return SurfaceMesh(vertices, new_faces)
