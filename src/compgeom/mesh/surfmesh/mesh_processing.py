"""Mesh processing algorithms: smoothing and hole filling."""
from collections import defaultdict
from typing import List, Tuple, Set

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MeshProcessing:
    """Algorithms that modify the mesh geometry or topology."""

    @staticmethod
    def laplacian_smoothing(mesh: TriangleMesh, iterations: int = 1, lambda_factor: float = 0.5) -> TriangleMesh:
        """Applies uniform Laplacian smoothing to interior vertices."""
        vertices = mesh.vertices
        faces = mesh.faces
        
        # Build adjacency
        adj = defaultdict(set)
        for face in faces:
            for i in range(3):
                u, v = face[i], face[(i+1)%3]
                adj[u].add(v)
                adj[v].add(u)
                
        # Identify boundary vertices to keep them fixed
        edge_counts = defaultdict(int)
        for face in faces:
            for i in range(3):
                edge = tuple(sorted((face[i], face[(i+1)%3])))
                edge_counts[edge] += 1
                
        boundary_vertices = set()
        for edge, count in edge_counts.items():
            if count == 1:
                boundary_vertices.update(edge)
                
        new_vertices = [Point3D(v.x, v.y, getattr(v, 'z', 0.0)) for v in vertices]
        
        for _ in range(iterations):
            temp_vertices = []
            for i, v in enumerate(new_vertices):
                if i in boundary_vertices or not adj[i]:
                    temp_vertices.append(Point3D(v.x, v.y, getattr(v, 'z', 0.0)))
                    continue
                    
                sum_x = sum_y = sum_z = 0.0
                neighbors = adj[i]
                for n in neighbors:
                    nv = new_vertices[n]
                    sum_x += nv.x
                    sum_y += nv.y
                    sum_z += getattr(nv, 'z', 0.0)
                    
                n_count = len(neighbors)
                avg_x = sum_x / n_count
                avg_y = sum_y / n_count
                avg_z = sum_z / n_count
                
                nx = v.x + lambda_factor * (avg_x - v.x)
                ny = v.y + lambda_factor * (avg_y - v.y)
                nz = getattr(v, 'z', 0.0) + lambda_factor * (avg_z - getattr(v, 'z', 0.0))
                temp_vertices.append(Point3D(nx, ny, nz))
            new_vertices = temp_vertices
            
        return TriangleMesh(new_vertices, faces)

    @staticmethod
    def fill_holes(mesh: TriangleMesh) -> TriangleMesh:
        """Fills boundary holes by connecting boundary loops to their centroids."""
        # Detect boundary edges
        edge_counts = defaultdict(int)
        edge_to_directed = {}
        for face in mesh.faces:
            for i in range(3):
                u, v = face[i], face[(i+1)%3]
                edge = tuple(sorted((u, v)))
                edge_counts[edge] += 1
                # Forward edge direction for outward pointing normal assumption
                edge_to_directed[edge] = (u, v)
                
        boundary_edges = [edge_to_directed[e] for e, c in edge_counts.items() if c == 1]
        if not boundary_edges:
            return mesh # No holes
            
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
                sum_z += getattr(v, 'z', 0.0)
            
            centroid = Point3D(sum_x/len(loop), sum_y/len(loop), sum_z/len(loop))
            c_idx = len(vertices)
            vertices.append(centroid)
            
            # Connect loop to centroid
            for i in range(len(loop)):
                u = loop[i]
                v = loop[(i+1)%len(loop)]
                new_faces.append((u, v, c_idx))
                
    @staticmethod
    def taubin_smoothing(mesh: TriangleMesh, iterations: int = 10, lambda_factor: float = 0.5, mu_factor: float = -0.53) -> TriangleMesh:
        """
        Applies non-shrinking smoothing using the Taubin (lambda-mu) algorithm.
        Typically, lambda > 0 and mu < -lambda.
        """
        current_mesh = mesh
        for _ in range(iterations):
            # Step 1: Smoothing (shrinking)
            current_mesh = MeshProcessing.laplacian_smoothing(current_mesh, iterations=1, lambda_factor=lambda_factor)
            # Step 2: Un-smoothing (expanding)
            current_mesh = MeshProcessing.laplacian_smoothing(current_mesh, iterations=1, lambda_factor=mu_factor)
        return current_mesh

    @staticmethod
    def loop_subdivision(mesh: TriangleMesh, iterations: int = 1) -> TriangleMesh:
        """
        Applies Loop subdivision to refine the mesh and smooth its surface.
        Each triangle is split into four smaller triangles.
        """
        import math
        current_mesh = mesh
        
        for _ in range(iterations):
            old_verts = current_mesh.vertices
            old_faces = current_mesh.faces
            
            # 1. Collect adjacency info
            edge_to_faces = defaultdict(list)
            v_adj = defaultdict(set)
            for f_idx, face in enumerate(old_faces):
                for i in range(3):
                    u, v = sorted((face[i], face[(i+1)%3]))
                    edge_to_faces[(u, v)].append(f_idx)
                    v_adj[face[i]].add(face[(i+1)%3])
                    v_adj[face[(i+1)%3]].add(face[i])
            
            # 2. Compute new vertices for each edge
            edge_new_vert = {}
            new_verts = [None] * len(old_verts) # Will be populated with updated old verts
            
            for (u, v), incident_faces in edge_to_faces.items():
                p_u = old_verts[u]
                p_v = old_verts[v]
                
                if len(incident_faces) == 2:
                    # Interior edge
                    # Find the opposite vertices in the two incident faces
                    opp = []
                    for f_idx in incident_faces:
                        for idx in old_faces[f_idx]:
                            if idx != u and idx != v:
                                opp.append(idx)
                    
                    p_c, p_d = old_verts[opp[0]], old_verts[opp[1]]
                    
                    nx = (3/8) * (p_u.x + p_v.x) + (1/8) * (p_c.x + p_d.x)
                    ny = (3/8) * (p_u.y + p_v.y) + (1/8) * (p_c.y + p_d.y)
                    nz = (3/8) * (getattr(p_u, 'z', 0.0) + getattr(p_v, 'z', 0.0)) + \
                         (1/8) * (getattr(p_c, 'z', 0.0) + getattr(p_d, 'z', 0.0))
                    edge_new_vert[(u, v)] = len(old_verts) + len(edge_new_vert)
                    new_verts.append(Point3D(nx, ny, nz))
                else:
                    # Boundary edge
                    nx = 0.5 * (p_u.x + p_v.x)
                    ny = 0.5 * (p_u.y + p_v.y)
                    nz = 0.5 * (getattr(p_u, 'z', 0.0) + getattr(p_v, 'z', 0.0))
                    edge_new_vert[(u, v)] = len(old_verts) + len(edge_new_vert)
                    new_verts.append(Point3D(nx, ny, nz))

            # 3. Update old vertex positions
            for i, p in enumerate(old_verts):
                neighbors = v_adj[i]
                n = len(neighbors)
                
                # Check if boundary vertex
                is_boundary = False
                boundary_neighbors = []
                for neighbor in neighbors:
                    edge = tuple(sorted((i, neighbor)))
                    if len(edge_to_faces[edge]) == 1:
                        is_boundary = True
                        boundary_neighbors.append(neighbor)
                
                if is_boundary:
                    # Boundary rule: 3/4 * V + 1/8 * sum(boundary_neighbors)
                    if len(boundary_neighbors) == 2:
                        nb1, nb2 = old_verts[boundary_neighbors[0]], old_verts[boundary_neighbors[1]]
                        nx = 0.75 * p.x + 0.125 * (nb1.x + nb2.x)
                        ny = 0.75 * p.y + 0.125 * (nb1.y + nb2.y)
                        nz = 0.75 * getattr(p, 'z', 0.0) + 0.125 * (getattr(nb1, 'z', 0.0) + getattr(nb2, 'z', 0.0))
                        new_verts[i] = Point3D(nx, ny, nz)
                    else:
                        new_verts[i] = Point3D(p.x, p.y, getattr(p, 'z', 0.0))
                else:
                    # Interior rule
                    # Beta = 1/n * (5/8 - (3/8 + 1/4*cos(2*pi/n))^2)
                    beta = (1/n) * (5/8 - (3/8 + 0.25 * math.cos(2 * math.pi / n))**2)
                    
                    sum_x = sum_y = sum_z = 0.0
                    for nb_idx in neighbors:
                        nb = old_verts[nb_idx]
                        sum_x += nb.x
                        sum_y += nb.y
                        sum_z += getattr(nb, 'z', 0.0)
                    
                    nx = (1 - n * beta) * p.x + beta * sum_x
                    ny = (1 - n * beta) * p.y + beta * sum_y
                    nz = (1 - n * beta) * getattr(p, 'z', 0.0) + beta * sum_z
                    new_verts[i] = Point3D(nx, ny, nz)

            # 4. Construct new faces
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
                
            current_mesh = TriangleMesh(new_verts, new_faces)
            
        return current_mesh
