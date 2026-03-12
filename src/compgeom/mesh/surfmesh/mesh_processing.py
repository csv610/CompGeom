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
                
        return TriangleMesh(vertices, new_faces)
