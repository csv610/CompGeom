"""Geodesic distance calculations on surface meshes."""
import heapq
import math
from collections import defaultdict
from typing import List, Dict, Tuple

from compgeom.mesh import TriMesh
from compgeom.kernel import Point3D

class MeshGeodesics:
    """Calculates distances along the surface of a mesh."""

    @staticmethod
    def get_adjacency_list(mesh: TriMesh) -> Dict[int, List[Tuple[int, float]]]:
        """Builds adjacency list with unique edge lengths."""
        adj = defaultdict(list)
        processed_edges = set()
        for face in mesh.faces:
            for i in range(3):
                u, v = face[i], face[(i+1)%3]
                edge = tuple(sorted((u, v)))
                if edge not in processed_edges:
                    processed_edges.add(edge)
                    p_u, p_v = mesh.vertices[u], mesh.vertices[v]
                    dist = math.dist((p_u.x, p_u.y, getattr(p_u, 'z', 0.0)),
                                     (p_v.x, p_v.y, getattr(p_v, 'z', 0.0)))
                    adj[u].append((v, dist))
                    adj[v].append((u, dist))
        return adj

    @staticmethod
    def get_vertex_to_faces(mesh: TriMesh) -> Dict[int, List[int]]:
        """Maps each vertex index to a list of incident face indices."""
        v2f = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for v in face:
                v2f[v].append(i)
        return v2f

    @staticmethod
    def compute_distances(mesh: TriMesh, source_vertex_idx: int) -> List[float]:
        """
        Computes approximate geodesic distances from a source vertex to all other vertices
        using Dijkstra's algorithm along the mesh edges.
        """
        distances, _ = MeshGeodesics._dijkstra(mesh, source_vertex_idx)
        return distances

    @staticmethod
    def compute_geodesic_path(mesh: TriMesh, source_vertex_idx: int, target_vertex_idx: int) -> Tuple[float, List[int]]:
        """
        Computes the shortest path along the mesh edges from a source vertex to a target vertex.
        Returns a tuple containing the distance and the list of vertex indices forming the path.
        """
        distances, predecessors = MeshGeodesics._dijkstra(mesh, source_vertex_idx, target_vertex_idx)
        
        path = []
        if distances[target_vertex_idx] == float('inf'):
            return float('inf'), path
            
        curr = target_vertex_idx
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
            
        return distances[target_vertex_idx], path[::-1]

    @staticmethod
    def compute_distances_fmm(mesh: TriMesh, source_vertex_idx: int) -> List[float]:
        """
        Computes accurate geodesic distances from a source vertex using the Fast Marching Method.
        """
        distances, _ = MeshGeodesics._fmm(mesh, source_vertex_idx)
        return distances

    @staticmethod
    def compute_geodesic_path_fmm(mesh: TriMesh, source_vertex_idx: int, target_vertex_idx: int) -> Tuple[float, List[int]]:
        """
        Computes accurate geodesic distance and approximate path using FMM and Dijkstra-backtracking.
        """
        distances, predecessors = MeshGeodesics._fmm(mesh, source_vertex_idx, target_vertex_idx)
        
        path = []
        if distances[target_vertex_idx] == float('inf'):
            return float('inf'), path
            
        curr = target_vertex_idx
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
            
        return distances[target_vertex_idx], path[::-1]

    @staticmethod
    def compute_distance_field(mesh: TriMesh, source_vertex_idx: int, location: str = 'vertex', method: str = 'fmm') -> List[float]:
        """
        Calculates a geodesic distance field across the mesh starting from a source vertex.
        
        Args:
            mesh: The TriMesh.
            source_vertex_idx: Index of the source vertex.
            location: Where to compute distances: 'vertex' (nodes) or 'face' (cell centers).
            method: The algorithm to use: 'fmm' (Fast Marching Method, accurate) or 'dijkstra' (edge-based, fast).
            
        Returns:
            List of distances (floats). Length is num_vertices if location='vertex', num_faces if location='face'.
        """
        if method.lower() == 'fmm':
            vertex_distances, _ = MeshGeodesics._fmm(mesh, source_vertex_idx)
        elif method.lower() == 'dijkstra':
            vertex_distances, _ = MeshGeodesics._dijkstra(mesh, source_vertex_idx)
        else:
            raise ValueError(f"Unknown method: {method}. Choose 'fmm' or 'dijkstra'.")
            
        if location.lower() == 'vertex':
            return vertex_distances
        elif location.lower() == 'face':
            return MeshGeodesics.compute_face_distances(mesh, vertex_distances)
        else:
            raise ValueError(f"Unknown location: {location}. Choose 'vertex' or 'face'.")

    @staticmethod
    def compute_face_distances(mesh: TriMesh, vertex_distances: List[float]) -> List[float]:
        """
        Computes distances at face centroids (cell centers) by averaging their vertex distances.
        """
        face_distances = []
        for face in mesh.faces:
            # Average of distances at the three vertices of the triangle
            d1, d2, d3 = vertex_distances[face[0]], vertex_distances[face[1]], vertex_distances[face[2]]
            face_distances.append((d1 + d2 + d3) / 3.0)
        return face_distances

    @staticmethod
    def sort_vertices_by_distance(mesh: TriMesh, source_vertex_idx: int, method: str = 'fmm') -> List[Tuple[int, float]]:
        """
        Sorts all vertices in the mesh by their geodesic distance from a source vertex.
        
        Returns:
            List of (vertex_index, distance) tuples, sorted by distance in ascending order.
        """
        distances = MeshGeodesics.compute_distance_field(mesh, source_vertex_idx, location='vertex', method=method)
        # Create (index, distance) pairs and sort them by distance
        indexed_distances = list(enumerate(distances))
        return sorted(indexed_distances, key=lambda x: x[1])

    @staticmethod
    def _fmm(mesh: TriMesh, source_idx: int, target_idx: int = None) -> Tuple[List[float], List[int]]:
        """
        Internal Fast Marching Method (FMM) implementation.
        """
        num_vertices = len(mesh.vertices)
        distances = [float('inf')] * num_vertices
        predecessors = [None] * num_vertices
        
        # Vertex states: 0: FAR, 1: TRIAL, 2: ACCEPTED
        state = [0] * num_vertices
        
        vertex_to_faces = MeshGeodesics.get_vertex_to_faces(mesh)
                
        distances[source_idx] = 0.0
        state[source_idx] = 2 # ACCEPTED
        
        pq = []
        
        # Initialize neighbors of source
        for face_idx in vertex_to_faces[source_idx]:
            face = mesh.faces[face_idx]
            others = [v for v in face if v != source_idx]
            for v in others:
                if state[v] != 2:
                    p_v, p_s = mesh.vertices[v], mesh.vertices[source_idx]
                    d_v = math.dist((p_v.x, p_v.y, getattr(p_v, 'z', 0.0)),
                                    (p_s.x, p_s.y, getattr(p_s, 'z', 0.0)))
                    if d_v < distances[v]:
                        distances[v] = d_v
                        predecessors[v] = source_idx
                        if state[v] == 0:
                            state[v] = 1 # TRIAL
                            heapq.heappush(pq, (d_v, v))
        
        while pq:
            d_curr, u = heapq.heappop(pq)
            
            if d_curr > distances[u]:
                continue
                
            state[u] = 2 # ACCEPTED
            
            if target_idx is not None and u == target_idx:
                break
                
            # Update neighbors
            for face_idx in vertex_to_faces[u]:
                face = mesh.faces[face_idx]
                for v_idx in range(3):
                    v = face[v_idx]
                    if state[v] == 2:
                        continue
                        
                    v1 = face[(v_idx + 1) % 3]
                    v2 = face[(v_idx + 2) % 3]
                    
                    new_dist = float('inf')
                    best_pred = predecessors[v]
                    
                    # Case 1: Update using u and v1 (if v1 is ACCEPTED and distinct from u)
                    if state[v1] == 2 and v1 != u:
                        d_v_tri = MeshGeodesics._solve_local_eikonal(mesh.vertices[v], mesh.vertices[u], mesh.vertices[v1], distances[u], distances[v1])
                        if d_v_tri < new_dist:
                            new_dist = d_v_tri
                            best_pred = u
                            
                    # Case 2: Update using u and v2 (if v2 is ACCEPTED and distinct from u)
                    if state[v2] == 2 and v2 != u:
                        d_v_tri = MeshGeodesics._solve_local_eikonal(mesh.vertices[v], mesh.vertices[u], mesh.vertices[v2], distances[u], distances[v2])
                        if d_v_tri < new_dist:
                            new_dist = d_v_tri
                            best_pred = u
                            
                    # Fallback/Base: Edge update from u
                    p_v, p_u = mesh.vertices[v], mesh.vertices[u]
                    d_edge = distances[u] + math.dist((p_v.x, p_v.y, getattr(p_v, 'z', 0.0)),
                                                     (p_u.x, p_u.y, getattr(p_u, 'z', 0.0)))
                    if d_edge < new_dist:
                        new_dist = d_edge
                        best_pred = u
                        
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        predecessors[v] = best_pred
                        if state[v] == 0:
                            state[v] = 1
                        heapq.heappush(pq, (new_dist, v))
                        
        return distances, predecessors

    @staticmethod
    def _solve_local_eikonal(p_c: Point3D, p_a: Point3D, p_b: Point3D, d_a: float, d_b: float) -> float:
        """
        Solves the local eikonal equation for point C using points A and B within a triangle face.
        Uses the approach from Kimmel and Sethian (1998).
        """
        # Coordinate system transformation: A=(0,0), B=(a,0), C=(b,c)
        # Handle 2D/3D points
        a_coords = (p_a.x, p_a.y, getattr(p_a, 'z', 0.0))
        b_coords = (p_b.x, p_b.y, getattr(p_b, 'z', 0.0))
        c_coords = (p_c.x, p_c.y, getattr(p_c, 'z', 0.0))
        
        # Vectors from A
        u = tuple(b_i - a_i for b_i, a_i in zip(b_coords, a_coords))
        v = tuple(c_i - a_i for c_i, a_i in zip(c_coords, a_coords))
        
        # Dot products
        dot_uu = sum(u_i**2 for u_i in u)
        dot_vv = sum(v_i**2 for v_i in v)
        dot_uv = sum(u_i * v_i for u_i, v_i in zip(u, v))
        
        # Local coordinates in triangle ABC
        a_len = math.sqrt(dot_uu)
        if a_len < 1e-12:
            return min(d_a + math.dist(c_coords, a_coords), d_b + math.dist(c_coords, b_coords))
            
        b_pos = (a_len, 0.0)
        c_x = dot_uv / a_len
        c_y = math.sqrt(max(0.0, dot_vv - c_x**2))
        
        # Solve quadratic: ||grad T|| = 1
        # T(x,y) = alpha*x + beta*y + d_a
        # At B: alpha*a_len + d_a = d_b  => alpha = (d_b - d_a) / a_len
        # alpha^2 + beta^2 = 1 => beta = sqrt(1 - alpha^2)
        
        alpha = (d_b - d_a) / a_len
        if abs(alpha) > 1.0:
            # Characteristic outside the cone of (A,B,C)
            return min(d_a + math.dist(c_coords, a_coords), d_b + math.dist(c_coords, b_coords))
            
        beta = math.sqrt(1.0 - alpha**2)
        d_c_tri = alpha * c_x + beta * c_y + d_a
        
        # Proper validity check:
        # The virtual source projection must be within the triangle wedge.
        # Check if the "virtual source" point S=(s_x, s_y) such that dist(C,S) = d_c_tri
        # and dist(A,S) = d_a, dist(B,S) = d_b.
        # From the linear update T(x,y) = alpha*x + beta*y + d_a:
        # grad T = (alpha, beta). The virtual source is at C - d_c_tri * grad T.
        # A simpler check: the update is valid if the source S of the wavefront 
        # lies within the cone formed by CA and CB.
        # More robustly: d_a < d_b + a_len and d_b < d_a + a_len (triangle inequality for distances)
        # AND the characteristic direction must come from within the triangle.
        
        # Valid update conditions (Kimmel & Sethian):
        # 1. d_c_tri > max(d_a, d_b)
        # 2. alpha * a_len < c_x * (d_b - d_a) / a_len  -- wait, simpler:
        
        # Using the condition: c_x / c_y < alpha / beta < (c_x - a_len) / c_y is wrong.
        # Correct condition for the projection of the gradient to fall within the angle:
        u_val = (d_b - d_a) / a_len
        v_val = (d_c_tri - d_a)
        
        # Check if the characteristic direction from C points into the triangle face:
        # The direction is -grad T = (-alpha, -beta).
        # It must be between vectors CA and CB.
        
        is_valid = False
        if d_c_tri > max(d_a, d_b):
            # Check if the update is "from the front" (within the triangle)
            # The condition is: a_len * c_x / (c_x**2 + c_y**2) < alpha < (c_x - a_len) / ...
            # Actually, the most robust check is testing the virtual source S:
            # S is at (c_x - (d_c_tri - d_a)*alpha, c_y - (d_c_tri - d_a)*beta) relative to A? No.
            
            # Let's use the robust condition:
            # u_val = d_b - d_a
            # if u_val < a_len:
            #   solve quadratic for d_c... (which we did)
            #   check if: a_len * (c_x * u_val - c_y * sqrt(a_len^2 - u_val^2)) < u_val * (c_x^2 + c_y^2) < ...
            
            # Let's simplify and use the condition from another stable implementation:
            cond1 = a_len * (d_c_tri - d_a) * alpha > (d_c_tri - d_a) * c_x - (c_y * math.sqrt(max(0.0, (d_c_tri - d_a)**2 - (alpha * c_x)**2)))
            # This is getting complex. Let's use the standard "angle" check.
            
            # The direction of propagation is grad T = (alpha, beta).
            # The update is valid if grad T, when placed at C, points AWAY from the face,
            # meaning the wavefront is MOVING into the face.
            # No, the characteristic must point from C INTO the triangle towards the edge AB.
            # Vector CA = (-c_x, -c_y), Vector CB = (a_len - c_x, -c_y).
            # grad T = (alpha, beta).
            # alpha * (-c_y) - beta * (-c_x) > 0  (one side of CA)
            # alpha * (-c_y) - beta * (a_len - c_x) < 0 (other side of CB)
            
            if (alpha * (-c_y) - beta * (-c_x) >= -1e-9) and (alpha * (-c_y) - beta * (a_len - c_x) <= 1e-9):
                is_valid = True
                
        if not is_valid:
            return min(d_a + math.dist(c_coords, a_coords), d_b + math.dist(c_coords, b_coords))
            
        return d_c_tri

    @staticmethod
    def _dijkstra(mesh: TriMesh, source_idx: int, target_idx: int = None) -> Tuple[List[float], List[int]]:
        """
        Internal Dijkstra implementation that optionally stops at target and returns predecessors.
        """
        num_vertices = len(mesh.vertices)
        distances = [float('inf')] * num_vertices
        predecessors = [None] * num_vertices
        distances[source_idx] = 0.0
        
        # Build adjacency list
        adj = MeshGeodesics.get_adjacency_list(mesh)
                
        pq = [(0.0, source_idx)]
        
        while pq:
            current_dist, current_u = heapq.heappop(pq)
            
            if current_dist > distances[current_u]:
                continue
                
            if target_idx is not None and current_u == target_idx:
                break
                
            for v, weight in adj[current_u]:
                distance = current_dist + weight
                if distance < distances[v]:
                    distances[v] = distance
                    predecessors[v] = current_u
                    heapq.heappush(pq, (distance, v))
                    
        return distances, predecessors
