"""Mesh subdivision algorithms."""

import math
from collections import defaultdict
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.kernel import Point3D


def loop_subdivision(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies Loop subdivision to refine the mesh and smooth its surface."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        edge_to_faces = defaultdict(list)
        v_adj = defaultdict(set)
        for f_idx, face in enumerate(old_faces):
            for i in range(3):
                u, v = sorted((face[i], face[(i + 1) % 3]))
                edge_to_faces[(u, v)].append(f_idx)
                v_adj[face[i]].add(face[(i + 1) % 3])
                v_adj[face[(i + 1) % 3]].add(face[i])

        edge_new_vert = {}
        new_verts = [None] * len(old_verts)

        for (u, v), incident_faces in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            if len(incident_faces) == 2:
                opp = []
                for f_idx in incident_faces:
                    for idx in old_faces[f_idx]:
                        if idx != u and idx != v:
                            opp.append(idx)
                p_c, p_d = old_verts[opp[0]], old_verts[opp[1]]
                nx = (3 / 8) * (p_u.x + p_v.x) + (1 / 8) * (p_c.x + p_d.x)
                ny = (3 / 8) * (p_u.y + p_v.y) + (1 / 8) * (p_c.y + p_d.y)
                nz = (3 / 8) * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0)) + (1 / 8) * (getattr(p_c, "z", 0.0) + getattr(p_d, "z", 0.0))
                edge_new_vert[(u, v)] = len(old_verts) + len(edge_new_vert)
                new_verts.append(Point3D(nx, ny, nz))
            else:
                nx = 0.5 * (p_u.x + p_v.x)
                ny = 0.5 * (p_u.y + p_v.y)
                nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
                edge_new_vert[(u, v)] = len(old_verts) + len(edge_new_vert)
                new_verts.append(Point3D(nx, ny, nz))

        for i, p in enumerate(old_verts):
            neighbors = v_adj[i]
            n = len(neighbors)
            is_boundary = False
            boundary_neighbors = []
            for neighbor in neighbors:
                edge = tuple(sorted((i, neighbor)))
                if len(edge_to_faces[edge]) == 1:
                    is_boundary = True
                    boundary_neighbors.append(neighbor)

            if is_boundary:
                if len(boundary_neighbors) == 2:
                    nb1, nb2 = old_verts[boundary_neighbors[0]], old_verts[boundary_neighbors[1]]
                    nx = 0.75 * p.x + 0.125 * (nb1.x + nb2.x)
                    ny = 0.75 * p.y + 0.125 * (nb1.y + nb2.y)
                    nz = 0.75 * getattr(p, "z", 0.0) + 0.125 * (getattr(nb1, "z", 0.0) + getattr(nb2, "z", 0.0))
                    new_verts[i] = Point3D(nx, ny, nz)
                else:
                    new_verts[i] = Point3D(p.x, p.y, getattr(p, "z", 0.0))
            else:
                beta = (1 / n) * (5 / 8 - (3 / 8 + 0.25 * math.cos(2 * math.pi / n)) ** 2)
                sum_x = sum_y = sum_z = 0.0
                for nb_idx in neighbors:
                    nb = old_verts[nb_idx]
                    sum_x += nb.x
                    sum_y += nb.y
                    sum_z += getattr(nb, "z", 0.0)
                nx = (1 - n * beta) * p.x + beta * sum_x
                ny = (1 - n * beta) * p.y + beta * sum_y
                nz = (1 - n * beta) * getattr(p, "z", 0.0) + beta * sum_z
                new_verts[i] = Point3D(nx, ny, nz)

        new_faces = []
        for face in old_faces:
            v0, v1, v2 = face
            e01 = edge_new_vert[tuple(sorted((v0, v1)))]
            e12 = edge_new_vert[tuple(sorted((v1, v2)))]
            e20 = edge_new_vert[tuple(sorted((v2, v0)))]
            new_faces.append((v0, e01, e20))
            new_faces.append((v1, e12, e01))
            new_faces.append((v2, e20, e12))
            new_faces.append((e01, e12, e20))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def catmull_clark(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies Catmull-Clark subdivision."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        edge_to_faces = defaultdict(list)
        v_edges = defaultdict(list)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            n = len(v_indices)
            for i in range(n):
                u, v = v_indices[i], v_indices[(i + 1) % n]
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(f_idx)
                v_edges[u].append(edge)
                v_edges[v].append(edge)

        face_points = {}
        for f_idx, face in enumerate(old_faces):
            vs = [old_verts[i] for i in face.v_indices]
            cx = sum(v.x for v in vs) / len(vs)
            cy = sum(v.y for v in vs) / len(vs)
            cz = sum(getattr(v, "z", 0.0) for v in vs) / len(vs)
            face_points[f_idx] = Point3D(cx, cy, cz)

        edge_points = {}
        for (u, v), incident in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            if len(incident) == 2:
                p_f1 = face_points[incident[0]]
                p_f2 = face_points[incident[1]]
                nx = (p_u.x + p_v.x + p_f1.x + p_f2.x) / 4
                ny = (p_u.y + p_v.y + p_f1.y + p_f2.y) / 4
                nz = (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0) + getattr(p_f1, "z", 0.0) + getattr(p_f2, "z", 0.0)) / 4
            else:
                nx = (p_u.x + p_v.x) / 2
                ny = (p_u.y + p_v.y) / 2
                nz = (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0)) / 2
            edge_points[(u, v)] = Point3D(nx, ny, nz)

        new_verts = list(old_verts)
        edge_point_indices = {}
        for (u, v), ep in edge_points.items():
            edge_point_indices[(u, v)] = len(new_verts)
            new_verts.append(ep)

        face_point_indices = {}
        for f_idx, fp in face_points.items():
            face_point_indices[f_idx] = len(new_verts)
            new_verts.append(fp)

        for v_idx, p in enumerate(old_verts):
            incident_edges = v_edges[v_idx]
            n = len(incident_edges)
            f_sum_x = f_sum_y = f_sum_z = 0.0
            r_sum_x = r_sum_y = r_sum_z = 0.0
            face_vertices = set()

            for edge in incident_edges:
                ep = edge_points[edge]
                r_sum_x += ep.x
                r_sum_y += ep.y
                r_sum_z += getattr(ep, "z", 0.0)
                for f_idx in edge_to_faces[edge]:
                    if f_idx not in face_vertices:
                        face_vertices.add(f_idx)
                        fp = face_points[f_idx]
                        f_sum_x += fp.x
                        f_sum_y += fp.y
                        f_sum_z += getattr(fp, "z", 0.0)

            if n == 0:
                new_verts[v_idx] = p
                continue

            f_avg_x = f_sum_x / n
            f_avg_y = f_sum_y / n
            f_avg_z = f_sum_z / n
            r_avg_x = r_sum_x / n
            r_avg_y = r_sum_y / n
            r_avg_z = r_sum_z / n

            nx = (f_avg_x + 2 * r_avg_x + (n - 3) * p.x) / n
            ny = (f_avg_y + 2 * r_avg_y + (n - 3) * p.y) / n
            nz = (f_avg_z + 2 * r_avg_z + (n - 3) * getattr(p, "z", 0.0)) / n
            new_verts[v_idx] = Point3D(nx, ny, nz)

        new_faces = []
        for f_idx, face in enumerate(old_faces):
            vs = list(face.v_indices)
            n = len(vs)
            fp_idx = face_point_indices[f_idx]
            ep_idxs = []
            for i in range(n):
                u, v = sorted((vs[i], vs[(i + 1) % n]))
                ep_idxs.append(edge_point_indices[(u, v)])
            for i in range(n):
                new_faces.append((fp_idx, ep_idxs[i], vs[(i + 1) % n], ep_idxs[(i + 1) % n]))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def doo_sabin(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies Doo-Sabin subdivision (dual scheme)."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        edge_to_faces = defaultdict(list)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            n = len(v_indices)
            for i in range(n):
                u, v = v_indices[i], v_indices[(i + 1) % n]
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(f_idx)

        new_face_vertices = {}
        for f_idx, face in enumerate(old_faces):
            vs = [old_verts[i] for i in face.v_indices]
            n = len(vs)
            alpha = 3.0 / 8.0 if n == 4 else (3.0 / 4.0) / (n * n)
            face_verts = []
            for i in range(n):
                vi = vs[i]
                vi1 = vs[(i + 1) % n]
                vi2 = vs[(i + 2) % n]
                nx = (1 - alpha) * vi.x + alpha * 0.5 * (vi1.x + vi2.x)
                ny = (1 - alpha) * vi.y + alpha * 0.5 * (vi1.y + vi2.y)
                nz = (1 - alpha) * getattr(vi, "z", 0.0) + alpha * 0.5 * (getattr(vi1, "z", 0.0) + getattr(vi2, "z", 0.0))
                face_verts.append(Point3D(nx, ny, nz))
            new_face_vertices[f_idx] = face_verts

        new_verts = list(old_verts)
        edge_point_indices = {}
        for (u, v), incident in edge_to_faces.items():
            ep_parts = []
            for f_idx in incident:
                face_verts = new_face_vertices[f_idx]
                v_idx_in_face = list(old_faces[f_idx].v_indices).index(u)
                ep_parts.append(face_verts[v_idx_in_face])
            if len(ep_parts) >= 2:
                p1, p2 = ep_parts[0], ep_parts[1]
                nx = 0.5 * (p1.x + p2.x)
                ny = 0.5 * (p1.y + p2.y)
                nz = 0.5 * (getattr(p1, "z", 0.0) + getattr(p2, "z", 0.0))
            else:
                nx = sum(p.x for p in ep_parts) / len(ep_parts)
                ny = sum(p.y for p in ep_parts) / len(ep_parts)
                nz = sum(getattr(p, "z", 0.0) for p in ep_parts) / len(ep_parts)
            edge_point_indices[(u, v)] = len(new_verts)
            new_verts.append(Point3D(nx, ny, nz))

        face_point_indices = {}
        for f_idx, fv in new_face_vertices.items():
            fp_start = len(new_verts)
            face_point_indices[f_idx] = fp_start
            for pv in fv:
                new_verts.append(pv)

        new_faces = []
        for f_idx, face in enumerate(old_faces):
            vs = list(face.v_indices)
            n = len(vs)
            fp_idx = face_point_indices[f_idx]
            ep_idxs = []
            for i in range(n):
                u, v = sorted((vs[i], vs[(i + 1) % n]))
                ep_idxs.append(edge_point_indices[(u, v)])
            for i in range(n):
                new_faces.append((fp_idx, ep_idxs[i], vs[(i + 1) % n], ep_idxs[(i + 1) % n]))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def sqrt3_subdivision(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies sqrt(3) subdivision to triangular meshes."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        v_adj = defaultdict(set)
        edge_to_faces = defaultdict(list)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                v_adj[u].add(v)
                v_adj[v].add(u)
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(f_idx)

        new_verts = list(old_verts)
        edge_to_midpoint = {}

        for (u, v), incident_faces in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            if len(incident_faces) == 2:
                opp = []
                for f_idx in incident_faces:
                    for idx in old_faces[f_idx].v_indices:
                        if idx != u and idx != v:
                            opp.append(idx)
                p_c, p_d = old_verts[opp[0]], old_verts[opp[1]]
                nx = 0.5 * (p_u.x + p_v.x) + 0.125 * (p_c.x - p_d.x)
                ny = 0.5 * (p_u.y + p_v.y) + 0.125 * (p_c.y - p_d.y)
                nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0)) + 0.125 * (getattr(p_c, "z", 0.0) - getattr(p_d, "z", 0.0))
            else:
                nx = 0.5 * (p_u.x + p_v.x)
                ny = 0.5 * (p_u.y + p_v.y)
                nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
            edge_to_midpoint[(u, v)] = len(new_verts)
            new_verts.append(Point3D(nx, ny, nz))

        for v_idx, p in enumerate(old_verts):
            neighbors = list(v_adj[v_idx])
            n = len(neighbors)
            is_boundary = any(len(edge_to_faces[tuple(sorted((v_idx, nb)))]) == 1 for nb in neighbors)

            if is_boundary:
                boundary_neighbors = [nb for nb in neighbors if len(edge_to_faces[tuple(sorted((v_idx, nb)))]) == 1]
                if len(boundary_neighbors) >= 2:
                    nb1, nb2 = old_verts[boundary_neighbors[0]], old_verts[boundary_neighbors[-1]]
                    nx = p.x + (1.0 / 3.0) * (nb1.x + nb2.x - 2 * p.x)
                    ny = p.y + (1.0 / 3.0) * (nb1.y + nb2.y - 2 * p.y)
                    nz = getattr(p, "z", 0.0) + (1.0 / 3.0) * (getattr(nb1, "z", 0.0) + getattr(nb2, "z", 0.0) - 2 * getattr(p, "z", 0.0))
                else:
                    nx, ny, nz = p.x, p.y, getattr(p, "z", 0.0)
            else:
                alpha = (1.0 / 3.0) * (4.0 - 2.0 * math.cos(2 * math.pi / n)) / n
                sum_x = sum(old_verts[nb].x for nb in neighbors)
                sum_y = sum(old_verts[nb].y for nb in neighbors)
                sum_z = sum(getattr(old_verts[nb], "z", 0.0) for nb in neighbors)
                nx = p.x + alpha * (sum_x / n - p.x)
                ny = p.y + alpha * (sum_y / n - p.y)
                nz = getattr(p, "z", 0.0) + alpha * (sum_z / n - getattr(p, "z", 0.0))
            new_verts[v_idx] = Point3D(nx, ny, nz)

        new_faces = []
        for f_idx, face in enumerate(old_faces):
            vs = list(face.v_indices)
            v0, v1, v2 = vs[0], vs[1], vs[2]
            e01 = edge_to_midpoint[tuple(sorted((v0, v1)))]
            e12 = edge_to_midpoint[tuple(sorted((v1, v2)))]
            e20 = edge_to_midpoint[tuple(sorted((v2, v0)))]
            new_faces.append((v0, e01, e20))
            new_faces.append((v1, e12, e01))
            new_faces.append((v2, e20, e12))
            new_faces.append((e01, e12, e20))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def butterfly_subdivision(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies Butterfly subdivision to triangular meshes."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        edge_to_faces = defaultdict(list)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(f_idx)

        edge_to_opposite = {}
        for (u, v), incident_faces in edge_to_faces.items():
            if len(incident_faces) == 2:
                opp = []
                for f_idx in incident_faces:
                    for idx in old_faces[f_idx].v_indices:
                        if idx != u and idx != v:
                            opp.append(idx)
                edge_to_opposite[(u, v)] = opp

        new_verts = list(old_verts)
        edge_new_vert = {}

        for (u, v), incident in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            if len(incident) == 2:
                opp = edge_to_opposite[(u, v)]
                p_c, p_d = old_verts[opp[0]], old_verts[opp[1]]
                nx = 0.5 * p_u.x + 0.5 * p_v.x + 0.125 * p_c.x + 0.125 * p_d.x
                ny = 0.5 * p_u.y + 0.5 * p_v.y + 0.125 * p_c.y + 0.125 * p_d.y
                nz = 0.5 * getattr(p_u, "z", 0.0) + 0.5 * getattr(p_v, "z", 0.0) + 0.125 * getattr(p_c, "z", 0.0) + 0.125 * getattr(p_d, "z", 0.0)
            else:
                nx = 0.5 * (p_u.x + p_v.x)
                ny = 0.5 * (p_u.y + p_v.y)
                nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
            edge_new_vert[(u, v)] = len(new_verts)
            new_verts.append(Point3D(nx, ny, nz))

        new_faces = []
        for face in old_faces:
            vs = list(face.v_indices)
            v0, v1, v2 = vs[0], vs[1], vs[2]
            e01 = edge_new_vert[tuple(sorted((v0, v1)))]
            e12 = edge_new_vert[tuple(sorted((v1, v2)))]
            e20 = edge_new_vert[tuple(sorted((v2, v0)))]
            new_faces.append((v0, e01, e20))
            new_faces.append((v1, e12, e01))
            new_faces.append((v2, e20, e12))
            new_faces.append((e01, e12, e20))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def modified_butterfly_subdivision(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies Modified Butterfly subdivision."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        v_adj = defaultdict(set)
        edge_to_faces = defaultdict(list)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            for i in range(3):
                u, v = v_indices[i], v_indices[(i + 1) % 3]
                v_adj[u].add(v)
                v_adj[v].add(u)
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(f_idx)

        edge_to_opposite = {}
        for (u, v), incident in edge_to_faces.items():
            if len(incident) == 2:
                opp = []
                for f_idx in incident:
                    for idx in old_faces[f_idx].v_indices:
                        if idx != u and idx != v:
                            opp.append(idx)
                edge_to_opposite[(u, v)] = opp

        new_verts = list(old_verts)
        edge_new_vert = {}

        for (u, v), incident in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            if len(incident) == 2:
                opp = edge_to_opposite.get((u, v))
                if opp and len(opp) == 2:
                    p_c, p_d = old_verts[opp[0]], old_verts[opp[1]]
                    deg_u, deg_v = len(v_adj[u]), len(v_adj[v])
                    alpha = 1.0 / 8.0 if deg_u == 6 and deg_v == 6 else 1.0 / 8.0 * (1.0 + (deg_u + deg_v) / 12.0)
                    nx = 0.5 * p_u.x + 0.5 * p_v.x + alpha * p_c.x + (0.25 - alpha) * p_d.x
                    ny = 0.5 * p_u.y + 0.5 * p_v.y + alpha * p_c.y + (0.25 - alpha) * p_d.y
                    nz = 0.5 * getattr(p_u, "z", 0.0) + 0.5 * getattr(p_v, "z", 0.0) + alpha * getattr(p_c, "z", 0.0) + (0.25 - alpha) * getattr(p_d, "z", 0.0)
                else:
                    nx = 0.5 * (p_u.x + p_v.x)
                    ny = 0.5 * (p_u.y + p_v.y)
                    nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
            else:
                nx = 0.5 * (p_u.x + p_v.x)
                ny = 0.5 * (p_u.y + p_v.y)
                nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
            edge_new_vert[(u, v)] = len(new_verts)
            new_verts.append(Point3D(nx, ny, nz))

        new_faces = []
        for face in old_faces:
            vs = list(face.v_indices)
            v0, v1, v2 = vs[0], vs[1], vs[2]
            e01 = edge_new_vert[tuple(sorted((v0, v1)))]
            e12 = edge_new_vert[tuple(sorted((v1, v2)))]
            e20 = edge_new_vert[tuple(sorted((v2, v0)))]
            new_faces.append((v0, e01, e20))
            new_faces.append((v1, e12, e01))
            new_faces.append((v2, e20, e12))
            new_faces.append((e01, e12, e20))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def kobbelt_subdivision(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies Kobbelt subdivision to quad-based meshes."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        edge_to_faces = defaultdict(list)
        v_adj = defaultdict(set)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            n = len(v_indices)
            for i in range(n):
                u, v = v_indices[i], v_indices[(i + 1) % n]
                edge = tuple(sorted((u, v)))
                edge_to_faces[edge].append(f_idx)
                v_adj[u].add(v)
                v_adj[v].add(u)

        face_points = {}
        for f_idx, face in enumerate(old_faces):
            vs = [old_verts[i] for i in face.v_indices]
            cx = sum(v.x for v in vs) / len(vs)
            cy = sum(v.y for v in vs) / len(vs)
            cz = sum(getattr(v, "z", 0.0) for v in vs) / len(vs)
            face_points[f_idx] = Point3D(cx, cy, cz)

        edge_points = {}
        for (u, v), incident in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            if len(incident) == 2:
                p_f1 = face_points[incident[0]]
                p_f2 = face_points[incident[1]]
                nx = 0.5625 * (p_u.x + p_v.x) + 0.0625 * (p_f1.x + p_f2.x)
                ny = 0.5625 * (p_u.y + p_v.y) + 0.0625 * (p_f1.y + p_f2.y)
                nz = 0.5625 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0)) + 0.0625 * (getattr(p_f1, "z", 0.0) + getattr(p_f2, "z", 0.0))
            else:
                nx = 0.5 * (p_u.x + p_v.x)
                ny = 0.5 * (p_u.y + p_v.y)
                nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
            edge_points[(u, v)] = Point3D(nx, ny, nz)

        new_verts = list(old_verts)
        edge_point_indices = {}
        for (u, v), ep in edge_points.items():
            edge_point_indices[(u, v)] = len(new_verts)
            new_verts.append(ep)

        face_point_indices = {}
        for f_idx, fp in face_points.items():
            face_point_indices[f_idx] = len(new_verts)
            new_verts.append(fp)

        for v_idx, p in enumerate(old_verts):
            neighbors = list(v_adj[v_idx])
            n = len(neighbors)
            f_sum_x = f_sum_y = f_sum_z = 0.0
            e_sum_x = e_sum_y = e_sum_z = 0.0

            for nb in neighbors:
                edge = tuple(sorted((v_idx, nb)))
                ep = edge_points[edge]
                e_sum_x += ep.x
                e_sum_y += ep.y
                e_sum_z += getattr(ep, "z", 0.0)

            incident_faces = set()
            for nb in neighbors:
                edge = tuple(sorted((v_idx, nb)))
                for f_idx in edge_to_faces[edge]:
                    incident_faces.add(f_idx)

            for f_idx in incident_faces:
                fp = face_points[f_idx]
                f_sum_x += fp.x
                f_sum_y += fp.y
                f_sum_z += getattr(fp, "z", 0.0)

            if n == 0:
                new_verts[v_idx] = p
                continue

            n_f = len(incident_faces)
            if n == 4 and n_f == 4:
                nx = 0.0625 * p.x
                ny = 0.0625 * p.y
                nz = 0.0625 * getattr(p, "z", 0.0)
            else:
                f_avg_x = f_sum_x / n_f if n_f > 0 else p.x
                f_avg_y = f_sum_y / n_f if n_f > 0 else p.y
                f_avg_z = f_sum_z / n_f if n_f > 0 else getattr(p, "z", 0.0)
                e_avg_x = e_sum_x / n
                e_avg_y = e_sum_y / n
                e_avg_z = e_sum_z / n
                nx = 0.5 * p.x + 0.25 * e_avg_x + 0.25 * f_avg_x
                ny = 0.5 * p.y + 0.25 * e_avg_y + 0.25 * f_avg_y
                nz = 0.5 * getattr(p, "z", 0.0) + 0.25 * e_avg_z + 0.25 * f_avg_z
            new_verts[v_idx] = Point3D(nx, ny, nz)

        new_faces = []
        for f_idx, face in enumerate(old_faces):
            vs = list(face.v_indices)
            n = len(vs)
            fp_idx = face_point_indices[f_idx]
            ep_idxs = []
            for i in range(n):
                u, v = sorted((vs[i], vs[(i + 1) % n]))
                ep_idxs.append(edge_point_indices[(u, v)])
            for i in range(n):
                new_faces.append((fp_idx, ep_idxs[i], vs[(i + 1) % n], ep_idxs[(i + 1) % n]))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh


def midedge_subdivision(mesh: SurfaceMesh, iterations: int = 1) -> SurfaceMesh:
    """Applies mid-edge subdivision."""
    current_mesh = mesh
    for _ in range(iterations):
        old_verts = current_mesh.vertices
        old_faces = current_mesh.faces

        edge_to_faces = defaultdict(list)
        for f_idx, face in enumerate(old_faces):
            v_indices = face.v_indices
            n = len(v_indices)
            for i in range(n):
                u, v = sorted((v_indices[i], v_indices[(i + 1) % n]))
                edge_to_faces[(u, v)].append(f_idx)

        new_verts = list(old_verts)
        edge_to_midpoint = {}

        for (u, v), _ in edge_to_faces.items():
            p_u = old_verts[u]
            p_v = old_verts[v]
            nx = 0.5 * (p_u.x + p_v.x)
            ny = 0.5 * (p_u.y + p_v.y)
            nz = 0.5 * (getattr(p_u, "z", 0.0) + getattr(p_v, "z", 0.0))
            edge_to_midpoint[(u, v)] = len(new_verts)
            new_verts.append(Point3D(nx, ny, nz))

        new_faces = []
        for f_idx, face in enumerate(old_faces):
            vs = list(face.v_indices)
            n = len(vs)
            mid_idxs = []
            for i in range(n):
                u, v = sorted((vs[i], vs[(i + 1) % n]))
                mid_idxs.append(edge_to_midpoint[(u, v)])
            for i in range(n):
                new_faces.append((mid_idxs[i], vs[(i + 1) % n], mid_idxs[(i + 1) % n]))

        current_mesh = SurfaceMesh(new_verts, new_faces)
    return current_mesh