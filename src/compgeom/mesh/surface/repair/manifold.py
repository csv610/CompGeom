"""Functions for repairing manifold properties and removing intersections."""

from __future__ import annotations
from collections import defaultdict, deque
from typing import List, Tuple, Union

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point2D, Point3D
from compgeom.intersect import tri_tri_intersect


def _get_triangle_coords(
    mesh: TriMesh, face_idx: int
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
    face = mesh.faces[face_idx]
    v0 = mesh.vertices[face[0]]
    v1 = mesh.vertices[face[1]]
    v2 = mesh.vertices[face[2]]
    return (
        (v0.x, v1.x, v2.x),
        (v0.y, v1.y, v2.y),
        (getattr(v0, "z", 0.0), getattr(v1, "z", 0.0), getattr(v2, "z", 0.0)),
    )


def remove_self_intersections(mesh: TriMesh) -> TriMesh:
    """Removes one of each pair of self-intersecting faces."""
    faces = mesh.faces
    vertices = mesh.vertices
    num_faces = len(faces)

    to_remove = set()
    aabbs = []
    for face in faces:
        pts = [vertices[idx] for idx in face]
        min_x = min(p.x for p in pts); max_x = max(p.x for p in pts)
        min_y = min(p.y for p in pts); max_y = max(p.y for p in pts)
        min_z = min(getattr(p, "z", 0.0) for p in pts); max_z = max(getattr(p, "z", 0.0) for p in pts)
        aabbs.append((min_x, max_x, min_y, max_y, min_z, max_z))

    for i in range(num_faces):
        if i in to_remove: continue
        for j in range(i + 1, num_faces):
            if j in to_remove: continue
            if len(set(faces[i]) & set(faces[j])) > 0: continue

            a1, a2 = aabbs[i], aabbs[j]
            if (a1[0] > a2[1] or a2[0] > a1[1] or a1[2] > a2[3] or a2[2] > a1[3] or a1[4] > a2[5] or a2[4] > a1[5]):
                continue

            tri1_pts = [vertices[idx] for idx in faces[i]]
            tri2_pts = [vertices[idx] for idx in faces[j]]

            if tri_tri_intersect(tri1_pts, tri2_pts):
                to_remove.add(j)

    new_faces = [faces[i] for i in range(num_faces) if i not in to_remove]
    return TriMesh(vertices, new_faces)


def remove_degenerate_faces(mesh: TriMesh) -> TriMesh:
    """Removes faces with zero area or duplicate vertices."""
    new_faces = []
    for face in mesh.faces:
        if len(set(face)) == 3:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            ux, uy, uz = v1.x - v0.x, v1.y - v0.y, getattr(v1, "z", 0.0) - getattr(v0, "z", 0.0)
            vx, vy, vz = v2.x - v0.x, v2.y - v0.y, getattr(v2, "z", 0.0) - getattr(v0, "z", 0.0)
            cx = uy * vz - uz * vy
            cy = uz * vx - ux * vz
            cz = ux * vy - uy * vx
            area_sq = cx * cx + cy * cy + cz * cz
            if area_sq > 1e-18: new_faces.append(face)
    return TriMesh(mesh.vertices, new_faces)


def remove_non_manifold_faces(mesh: TriMesh) -> TriMesh:
    """Removes faces attached to edges shared by more than two faces."""
    faces = mesh.faces
    edge_to_faces = defaultdict(list)
    for i, face in enumerate(faces):
        for j in range(3):
            u, v = sorted((face[j], face[(j + 1) % 3]))
            edge_to_faces[(u, v)].append(i)

    to_remove = set()
    for sharing_faces in edge_to_faces.values():
        if len(sharing_faces) > 2: to_remove.update(sharing_faces)

    new_faces = [faces[i] for i in range(len(faces)) if i not in to_remove]
    return TriMesh(mesh.vertices, new_faces)


def remove_non_manifold_vertices(mesh: TriMesh) -> TriMesh:
    """Removes faces to ensure no vertex is non-manifold."""
    faces = mesh.faces
    if not faces: return mesh
    v2f = defaultdict(list)
    for i, face in enumerate(faces):
        for v in face: v2f[v].append(i)
    to_remove = set()
    for incident_faces in v2f.values():
        if len(incident_faces) <= 1: continue
        adj = defaultdict(list)
        for i, f1_idx in enumerate(incident_faces):
            f1 = set(faces[f1_idx])
            for j in range(i + 1, len(incident_faces)):
                f2_idx = incident_faces[j]
                f2 = set(faces[f2_idx])
                if len(f1 & f2) == 2:
                    adj[f1_idx].append(f2_idx); adj[f2_idx].append(f1_idx)
        visited = set()
        components = []
        for f_idx in incident_faces:
            if f_idx in visited: continue
            comp, queue = [], deque([f_idx]); visited.add(f_idx)
            while queue:
                curr = queue.popleft(); comp.append(curr)
                for nxt in adj[curr]:
                    if nxt not in visited: visited.add(nxt); queue.append(nxt)
            components.append(comp)
        if len(components) > 1:
            components.sort(key=len, reverse=True)
            for comp in components[1:]: to_remove.update(comp)
    if not to_remove: return mesh
    new_faces = [f for i, f in enumerate(faces) if i not in to_remove]
    return TriMesh(mesh.vertices, new_faces)
