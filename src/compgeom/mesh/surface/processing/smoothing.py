"""Mesh smoothing algorithms."""

import math
from collections import defaultdict
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D

def laplacian_smoothing(
    mesh: SurfaceMesh, iterations: int = 1, lambda_factor: float = 0.5
) -> SurfaceMesh:
    """Applies uniform Laplacian smoothing to interior vertices."""
    vertices = mesh.vertices
    faces = mesh.faces

    # Build adjacency
    adj = defaultdict(set)
    for face in faces:
        for i in range(3):
            u, v = face[i], face[(i + 1) % 3]
            adj[u].add(v)
            adj[v].add(u)

    # Identify boundary vertices to keep them fixed
    edge_counts = defaultdict(int)
    for face in faces:
        for i in range(3):
            edge = tuple(sorted((face[i], face[(i + 1) % 3])))
            edge_counts[edge] += 1

    boundary_vertices = set()
    for edge, count in edge_counts.items():
        if count == 1:
            boundary_vertices.update(edge)

    new_vertices = [Point3D(v.x, v.y, getattr(v, "z", 0.0)) for v in vertices]

    for _ in range(iterations):
        temp_vertices = []
        for i, v in enumerate(new_vertices):
            if i in boundary_vertices or not adj[i]:
                temp_vertices.append(Point3D(v.x, v.y, getattr(v, "z", 0.0)))
                continue

            sum_x = sum_y = sum_z = 0.0
            neighbors = adj[i]
            for n in neighbors:
                nv = new_vertices[n]
                sum_x += nv.x
                sum_y += nv.y
                sum_z += getattr(nv, "z", 0.0)

            n_count = len(neighbors)
            avg_x = sum_x / n_count
            avg_y = sum_y / n_count
            avg_z = sum_z / n_count

            nx = v.x + lambda_factor * (avg_x - v.x)
            ny = v.y + lambda_factor * (avg_y - v.y)
            nz = getattr(v, "z", 0.0) + lambda_factor * (
                avg_z - getattr(v, "z", 0.0)
            )
            temp_vertices.append(Point3D(nx, ny, nz))
        new_vertices = temp_vertices

    return SurfaceMesh(new_vertices, faces)

def bilateral_smoothing(
    mesh: SurfaceMesh,
    iterations: int = 1,
    sigma_c: float = 1.0,
    sigma_s: float = 0.1,
) -> SurfaceMesh:
    """
    Applies feature-preserving bilateral smoothing to the mesh.
    sigma_c: Spatial neighborhood variance (influences how far neighbors affect smoothing)
    sigma_s: Signal variance (influences how much normals/features affect smoothing)
    """
    from compgeom.mesh.surface.mesh_analysis import MeshAnalysis

    vertices = list(mesh.vertices)
    faces = mesh.faces

    # Build vertex-to-face and vertex-to-vertex adjacency
    v2f = defaultdict(list)
    adj = defaultdict(set)
    for i, face in enumerate(faces):
        for j in range(3):
            u, v = face[j], face[(j + 1) % 3]
            adj[u].add(v)
            adj[v].add(u)
            v2f[u].append(i)
            v2f[v].append(i)
            v2f[face[(j + 2) % 3]].append(i)

    new_vertices = [Point3D(v.x, v.y, getattr(v, "z", 0.0)) for v in vertices]

    for _ in range(iterations):
        # Recompute normals at each iteration
        temp_mesh = SurfaceMesh(new_vertices, faces)
        v_normals = MeshAnalysis.compute_vertex_normals(temp_mesh)

        temp_verts = []
        for i, p in enumerate(new_vertices):
            n_i = v_normals[i]
            sum_w = 0.0
            sum_delta = 0.0

            for nb in adj[i]:
                q = new_vertices[nb]
                # Spatial distance
                t = math.sqrt(
                    (p.x - q.x) ** 2
                    + (p.y - q.y) ** 2
                    + (getattr(p, "z", 0.0) - getattr(q, "z", 0.0)) ** 2
                )
                # Height/normal distance (projection of (p-q) onto normal)
                h = (
                    (q.x - p.x) * n_i[0]
                    + (q.y - p.y) * n_i[1]
                    + (getattr(q, "z", 0.0) - getattr(p, "z", 0.0)) * n_i[2]
                )

                wc = math.exp(-(t**2) / (2 * sigma_c**2))
                ws = math.exp(-(h**2) / (2 * sigma_s**2))
                w = wc * ws

                sum_w += w
                sum_delta += w * h

            if sum_w > 1e-9:
                delta = sum_delta / sum_w
                nx = p.x + n_i[0] * delta
                ny = p.y + n_i[1] * delta
                nz = getattr(p, "z", 0.0) + n_i[2] * delta
                temp_verts.append(Point3D(nx, ny, nz))
            else:
                temp_verts.append(Point3D(p.x, p.y, getattr(p, "z", 0.0)))

        new_vertices = temp_verts

    return SurfaceMesh(new_vertices, faces)

def taubin_smoothing(
    mesh: SurfaceMesh,
    iterations: int = 10,
    lambda_factor: float = 0.5,
    mu_factor: float = -0.53,
) -> SurfaceMesh:
    """
    Applies non-shrinking smoothing using the Taubin (lambda-mu) algorithm.
    Typically, lambda > 0 and mu < -lambda.
    """
    current_mesh = mesh
    for _ in range(iterations):
        # Step 1: Smoothing (shrinking)
        current_mesh = laplacian_smoothing(
            current_mesh, iterations=1, lambda_factor=lambda_factor
        )
        # Step 2: Un-smoothing (expanding)
        current_mesh = laplacian_smoothing(
            current_mesh, iterations=1, lambda_factor=mu_factor
        )
    return current_mesh
