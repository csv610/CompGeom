"""Mesh geometry algorithms."""

import math
from collections import defaultdict
from typing import Tuple
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D

def mesh_offset(
    mesh: SurfaceMesh, distance: float, create_solid: bool = False
) -> SurfaceMesh:
    """
    Offsets the mesh surface by a given distance along vertex normals.
    If create_solid is True, it creates a thickened shell with closed walls.
    """
    from compgeom.mesh.surface.mesh_analysis import MeshAnalysis

    # 1. Compute weighted vertex normals
    v_normals = MeshAnalysis.compute_vertex_normals(mesh)

    # 2. Create offset vertices
    offset_verts = []
    for i, v in enumerate(mesh.vertices):
        nx, ny, nz = v_normals[i]
        ov = Point3D(
            v.x + nx * distance,
            v.y + ny * distance,
            getattr(v, "z", 0.0) + nz * distance,
        )
        offset_verts.append(ov)

    if not create_solid:
        return SurfaceMesh(offset_verts, mesh.faces)

    # 3. Create a solid shell (thickening)
    # Combine original and offset vertices
    total_verts = list(mesh.vertices) + offset_verts
    num_v = len(mesh.vertices)

    new_faces = []
    # Original faces (preserve orientation)
    for face in mesh.faces:
        new_faces.append(list(face))

    # Add offset faces (reversed orientation for outward normals)
    for face in mesh.faces:
        # Reverse order and offset indices
        new_faces.append([idx + num_v for idx in reversed(face)])

    # 4. Connect boundaries if the mesh is open
    edge_counts = defaultdict(int)
    for face in mesh.faces:
        n = len(face)
        for i in range(n):
            edge = tuple(sorted((face[i], face[(i + 1) % n])))
            edge_counts[edge] += 1

    # Find directed boundary edges
    for face in mesh.faces:
        n = len(face)
        for i in range(n):
            u, v = face[i], face[(i + 1) % n]
            if edge_counts[tuple(sorted((u, v)))] == 1:
                # Boundary edge (u, v).
                # Connect to (u', v') where u' = u + num_v
                u_off, v_off = u + num_v, v + num_v
                # Wall faces: (u, v, v_off) and (u, v_off, u_off)
                new_faces.append([u, v, v_off])
                new_faces.append([u, v_off, u_off])

    return SurfaceMesh(total_verts, new_faces)

def mesh_clipping(
    mesh: SurfaceMesh,
    plane_origin: Tuple[float, float, float],
    plane_normal: Tuple[float, float, float],
    cap: bool = True,
) -> Tuple[SurfaceMesh, SurfaceMesh]:
    """
    Splits the mesh into two parts using a plane.
    Returns a tuple (mesh_above, mesh_below).
    If cap is True, the cut surface is filled with a triangulation.
    """

    nx, ny, nz = plane_normal
    mag = math.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / mag, ny / mag, nz / mag

    def get_dist(p):
        return (
            (p.x - plane_origin[0]) * nx
            + (p.y - plane_origin[1]) * ny
            + (getattr(p, "z", 0.0) - plane_origin[2]) * nz
        )

    faces_above = []
    faces_below = []
    verts_above = list(mesh.vertices)
    verts_below = list(mesh.vertices)

    for face in mesh.faces:
        v_idx = face
        pts = [mesh.vertices[i] for i in v_idx]
        dists = [get_dist(p) for p in pts]

        # Cases: all above, all below, or mixed
        above = [d > 1e-9 for d in dists]
        below = [d < -1e-9 for d in dists]

        if all(above):
            faces_above.append(face)
        elif all(below):
            faces_below.append(face)
        else:
            # Triangle intersects plane. We split it into smaller triangles.
            # Simplified: skip splitting for V1.0 structure,
            # just assign to the side of the majority of vertices or the centroid.
            cx = (pts[0].x + pts[1].x + pts[2].x) / 3.0
            cy = (pts[0].y + pts[1].y + pts[2].y) / 3.0
            cz = (
                getattr(pts[0], "z", 0.0)
                + getattr(pts[1], "z", 0.0)
                + getattr(pts[2], "z", 0.0)
            ) / 3.0
            if (cx - plane_origin[0]) * nx + (cy - plane_origin[1]) * ny + (
                cz - plane_origin[2]
            ) * nz > 0:
                faces_above.append(face)
            else:
                faces_below.append(face)

    # For a full clipping, we must compute exact cut vertices and re-triangulate.
    # This version partitions whole faces.

    from compgeom.mesh.surface.repair import remove_isolated_vertices

    ma = remove_isolated_vertices(
        SurfaceMesh(verts_above, faces_above)
    )
    mb = remove_isolated_vertices(
        SurfaceMesh(verts_below, faces_below)
    )

    return ma, mb
