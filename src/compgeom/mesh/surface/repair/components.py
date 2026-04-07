"""Functions for removing small disconnected components from surface meshes."""

from __future__ import annotations

from collections import defaultdict, deque
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def remove_small_components(mesh: TriMesh, min_fraction: float = 0.05) -> TriMesh:
    """Removes disconnected components smaller than a threshold fraction."""
    faces = mesh.faces
    if not faces:
        return mesh

    edge_to_faces = defaultdict(list)
    for i, face in enumerate(faces):
        for j in range(3):
            u, v = sorted((face[j], face[(j + 1) % 3]))
            edge_to_faces[(u, v)].append(i)

    visited = [False] * len(faces)
    components = []

    for start_idx in range(len(faces)):
        if visited[start_idx]:
            continue

        comp_faces = []
        queue = deque([start_idx])
        visited[start_idx] = True

        while queue:
            curr_idx = queue.popleft()
            comp_faces.append(curr_idx)
            curr_face = faces[curr_idx]

            for i in range(3):
                u, v = sorted((curr_face[i], curr_face[(i + 1) % 3]))
                for neighbor_idx in edge_to_faces[(u, v)]:
                    if not visited[neighbor_idx]:
                        visited[neighbor_idx] = True
                        queue.append(neighbor_idx)

        components.append(comp_faces)

    if not components:
        return mesh

    max_len = max(len(c) for c in components)
    threshold = max(1, int(max_len * min_fraction))

    keep_faces = []
    for comp in components:
        if len(comp) >= threshold:
            keep_faces.extend(comp)

    new_faces = [faces[i] for i in keep_faces]
    return TriMesh(mesh.vertices, new_faces)
