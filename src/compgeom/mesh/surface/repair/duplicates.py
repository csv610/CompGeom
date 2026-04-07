"""Functions for removing duplicates and isolated elements from surface meshes."""

from __future__ import annotations

from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def remove_duplicate_points(mesh: TriMesh, epsilon: float = 1e-8) -> TriMesh:
    """Removes duplicate vertices and updates face indices."""
    old_vertices = mesh.vertices
    unique_vertices = []
    old_to_new = {}

    point_map = {}

    for i, v in enumerate(old_vertices):
        key = (
            round(v.x / epsilon),
            round(v.y / epsilon),
            round(getattr(v, "z", 0.0) / epsilon),
        )

        if key not in point_map:
            point_map[key] = len(unique_vertices)
            unique_vertices.append(v)

        old_to_new[i] = point_map[key]

    new_faces = []
    for face in mesh.faces:
        new_face = tuple(old_to_new[idx] for idx in face)
        if len(set(new_face)) == 3:
            new_faces.append(new_face)

    return TriMesh(unique_vertices, new_faces)


def remove_duplicate_faces(mesh: TriMesh) -> TriMesh:
    """Removes duplicate faces regardless of winding."""
    seen_faces = set()
    unique_faces = []

    for face in mesh.faces:
        sorted_face = tuple(sorted(face))
        if sorted_face not in seen_faces:
            seen_faces.add(sorted_face)
            unique_faces.append(face)

    return TriMesh(mesh.vertices, unique_faces)


def remove_isolated_vertices(mesh: TriMesh) -> TriMesh:
    """Removes vertices that are not referenced by any face."""
    used_indices = set()
    for face in mesh.faces:
        used_indices.update(face)

    if len(used_indices) == len(mesh.vertices):
        return mesh

    old_to_new = {}
    new_vertices = []
    for i, v in enumerate(mesh.vertices):
        if i in used_indices:
            old_to_new[i] = len(new_vertices)
            new_vertices.append(v)

    new_faces = [tuple(old_to_new[idx] for idx in face) for face in mesh.faces]
    return TriMesh(new_vertices, new_faces)
