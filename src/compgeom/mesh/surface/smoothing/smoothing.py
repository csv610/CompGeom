"""Mesh smoothing algorithms."""

import math
from collections import defaultdict
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D


def laplacian_smoothing(mesh: SurfaceMesh, iterations: int = 1, lambda_factor: float = 0.5) -> SurfaceMesh:
    """Applies uniform Laplacian smoothing to interior vertices."""
    vertices = mesh.vertices
    faces = mesh.faces

    adj = defaultdict(set)
    for face in faces:
        for i in range(3):
            u, v = face[i], face[(i + 1) % 3]
            adj[u].add(v)
            adj[v].add(u)

    edge_counts = defaultdict(int)
    for face in faces:
        for i in range(3):
            edge = tuple(sorted((face[i], face[(i + 1) % 3])))
            edge_counts[edge] += 1

    boundary_vertices = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted((face[i], face[(i + 1) % 3])))
            if edge_counts[edge] == 1:
                boundary_vertices.add(face[i])
                boundary_vertices.add(face[(i + 1) % 3])

    current_mesh = mesh
    for _ in range(iterations):
        verts = current_mesh.vertices
        new_verts = list(verts)

        for i, p in enumerate(verts):
            if i in boundary_vertices:
                new_verts[i] = p
                continue

            neighbors = list(adj[i])
            if not neighbors:
                continue

            nx = sum(verts[nb].x for nb in neighbors) / len(neighbors)
            ny = sum(verts[nb].y for nb in neighbors) / len(neighbors)
            nz = sum(getattr(verts[nb], "z", 0.0) for nb in neighbors) / len(neighbors)

            new_verts[i] = Point3D(
                p.x + lambda_factor * (nx - p.x),
                p.y + lambda_factor * (ny - p.y),
                getattr(p, "z", 0.0) + lambda_factor * (nz - getattr(p, "z", 0.0))
            )

        current_mesh = SurfaceMesh(new_verts, faces)

    return current_mesh


def bilateral_smoothing(mesh: SurfaceMesh, iterations: int = 1, sigma_d: float = 1.0, sigma_r: float = 1.0) -> SurfaceMesh:
    """Applies bilateral smoothing (edge-aware)."""
    faces = mesh.faces
    adj = defaultdict(set)
    for face in faces:
        for i in range(3):
            u, v = face[i], face[(i + 1) % 3]
            adj[u].add(v)
            adj[v].add(u)

    current_mesh = mesh
    for _ in range(iterations):
        verts = current_mesh.vertices
        new_verts = list(verts)

        for i, p in enumerate(verts):
            neighbors = list(adj[i])
            if len(neighbors) < 2:
                continue

            num = Point3D(0.0, 0.0, 0.0)
            den = 0.0

            for nb in neighbors:
                pb = verts[nb]
                dist = math.sqrt((p.x - pb.x) ** 2 + (p.y - pb.y) ** 2)
                weight = math.exp(-0.5 * (dist / sigma_d) ** 2)

                nx = pb.x - p.x
                ny = pb.y - p.y
                nz = getattr(pb, "z", 0.0) - getattr(p, "z", 0.0)
                weight_r = math.exp(-0.5 * (nx ** 2 + ny ** 2 + nz ** 2) / sigma_r ** 2)

                w = weight * weight_r
                num = Point3D(num.x + w * pb.x, num.y + w * pb.y, getattr(num, "z", 0.0) + w * getattr(pb, "z", 0.0))
                den += w

            if den > 0:
                new_verts[i] = Point3D(num.x / den, num.y / den, getattr(num, "z", 0.0) / den)

        current_mesh = SurfaceMesh(new_verts, faces)

    return current_mesh


def taubin_smoothing(mesh: SurfaceMesh, iterations: int = 1, lambda_factor: float = 0.5, mu_factor: float = 0.53) -> SurfaceMesh:
    """Applies Taubin smoothing (Laplacian + inverse)."""
    vertices = mesh.vertices
    faces = mesh.faces

    adj = defaultdict(set)
    for face in faces:
        for i in range(3):
            u, v = face[i], face[(i + 1) % 3]
            adj[u].add(v)
            adj[v].add(u)

    edge_counts = defaultdict(int)
    for face in faces:
        for i in range(3):
            edge = tuple(sorted((face[i], face[(i + 1) % 3])))
            edge_counts[edge] += 1

    boundary_vertices = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted((face[i], face[(i + 1) % 3])))
            if edge_counts[edge] == 1:
                boundary_vertices.add(face[i])
                boundary_vertices.add(face[(i + 1) % 3])

    current_mesh = mesh
    for _ in range(iterations):
        verts = current_mesh.vertices
        new_verts = list(verts)

        for i, p in enumerate(verts):
            if i in boundary_vertices:
                new_verts[i] = p
                continue

            neighbors = list(adj[i])
            if not neighbors:
                continue

            nx = sum(verts[nb].x for nb in neighbors) / len(neighbors)
            ny = sum(verts[nb].y for nb in neighbors) / len(neighbors)
            nz = sum(getattr(verts[nb], "z", 0.0) for nb in neighbors) / len(neighbors)

            new_verts[i] = Point3D(
                p.x + lambda_factor * (nx - p.x),
                p.y + lambda_factor * (ny - p.y),
                getattr(p, "z", 0.0) + lambda_factor * (nz - getattr(p, "z", 0.0))
            )

        new_verts, verts = list(new_verts), new_verts

        for i, p in enumerate(verts):
            if i in boundary_vertices:
                continue

            neighbors = list(adj[i])
            if not neighbors:
                continue

            nx = sum(verts[nb].x for nb in neighbors) / len(neighbors)
            ny = sum(verts[nb].y for nb in neighbors) / len(neighbors)
            nz = sum(getattr(verts[nb], "z", 0.0) for nb in neighbors) / len(neighbors)

            new_verts[i] = Point3D(
                p.x + mu_factor * (nx - p.x),
                p.y + mu_factor * (ny - p.y),
                getattr(p, "z", 0.0) + mu_factor * (nz - getattr(p, "z", 0.0))
            )

        current_mesh = SurfaceMesh(new_verts, faces)

    return current_mesh