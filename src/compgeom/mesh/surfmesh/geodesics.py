"""Geodesic distance calculations on surface meshes."""
import heapq
import math
from collections import defaultdict
from typing import List, Dict, Tuple

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MeshGeodesics:
    """Calculates distances along the surface of a mesh."""

    @staticmethod
    def compute_distances(mesh: TriangleMesh, source_vertex_idx: int) -> List[float]:
        """
        Computes approximate geodesic distances from a source vertex to all other vertices
        using Dijkstra's algorithm along the mesh edges.
        """
        num_vertices = len(mesh.vertices)
        distances = [float('inf')] * num_vertices
        distances[source_vertex_idx] = 0.0
        
        # Build adjacency list with edge lengths
        adj = defaultdict(list)
        for face in mesh.faces:
            for i in range(3):
                u, v = face[i], face[(i+1)%3]
                p_u, p_v = mesh.vertices[u], mesh.vertices[v]
                dist = math.sqrt((p_u.x - p_v.x)**2 + (p_u.y - p_v.y)**2 + (getattr(p_u, 'z', 0.0) - getattr(p_v, 'z', 0.0))**2)
                adj[u].append((v, dist))
                adj[v].append((u, dist))
                
        pq = [(0.0, source_vertex_idx)]
        
        while pq:
            current_dist, current_u = heapq.heappop(pq)
            
            if current_dist > distances[current_u]:
                continue
                
            for v, weight in adj[current_u]:
                distance = current_dist + weight
                if distance < distances[v]:
                    distances[v] = distance
                    heapq.heappush(pq, (distance, v))
                    
        return distances
