"""Functions for repairing normal orientations of surface meshes."""

from __future__ import annotations

from collections import defaultdict, deque
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def fix_normals(mesh: TriMesh) -> TriMesh:
    """Ensures all faces have consistent normal orientation using BFS."""
    faces = mesh.faces
    num_faces = len(faces)
    if num_faces == 0:
        return mesh

    edge_to_faces = defaultdict(list)
    for i, face in enumerate(faces):
        for j in range(3):
            u, v = face[j], face[(j + 1) % 3]
            edge = tuple(sorted((u, v)))
            edge_to_faces[edge].append(i)

    new_faces = [None] * num_faces
    visited = [False] * num_faces

    for start_idx in range(num_faces):
        if visited[start_idx]:
            continue

        queue = deque([start_idx])
        new_faces[start_idx] = faces[start_idx]
        visited[start_idx] = True

        while queue:
            curr_idx = queue.popleft()
            curr_face = new_faces[curr_idx]

            for i in range(3):
                u, v = curr_face[i], curr_face[(i + 1) % 3]
                edge = tuple(sorted((u, v)))

                for neighbor_idx in edge_to_faces[edge]:
                    if not visited[neighbor_idx]:
                        neighbor_face = list(faces[neighbor_idx])

                        for j in range(3):
                            nu, nv = neighbor_face[j], neighbor_face[(j + 1) % 3]
                            if {nu, nv} == {u, v}:
                                if nu == u:
                                    neighbor_face[0], neighbor_face[1] = (
                                        neighbor_face[1],
                                        neighbor_face[0],
                                    )

                                new_faces[neighbor_idx] = tuple(neighbor_face)
                                visited[neighbor_idx] = True
                                queue.append(neighbor_idx)
                                break

    final_faces = [f for f in new_faces if f is not None]
    return TriMesh(mesh.vertices, final_faces)


def orient_normals_outward(mesh: TriMesh) -> TriMesh:
    """Ensures normals for closed components point outward using signed volume."""
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

    new_faces = list(faces)
    vertices = mesh.vertices

    for comp in components:
        vol = 0.0
        for f_idx in comp:
            face = new_faces[f_idx]
            v0 = vertices[face[0]]
            v1 = vertices[face[1]]
            v2 = vertices[face[2]]

            p0 = (v0.x, v0.y, getattr(v0, "z", 0.0))
            p1 = (v1.x, v1.y, getattr(v1, "z", 0.0))
            p2 = (v2.x, v2.y, getattr(v2, "z", 0.0))

            cross_x = p1[1] * p2[2] - p1[2] * p2[1]
            cross_y = p1[2] * p2[0] - p1[0] * p2[2]
            cross_z = p1[0] * p2[1] - p1[1] * p2[0]

            vol += p0[0] * cross_x + p0[1] * cross_y + p0[2] * cross_z

        if vol < -1e-9:
            for f_idx in comp:
                f = new_faces[f_idx]
                new_faces[f_idx] = (f[0], f[2], f[1])

    return TriMesh(mesh.vertices, new_faces)
