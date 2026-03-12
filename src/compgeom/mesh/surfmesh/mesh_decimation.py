"""Mesh decimation using edge collapses."""
from __future__ import annotations
import heapq
from collections import defaultdict
from typing import List, Tuple, Dict, Set

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MeshDecimator:
    """Simplifies triangle meshes using Quadric Error Metrics (QEM)."""

    @staticmethod
    def decimate(mesh: TriangleMesh, target_faces: int) -> TriangleMesh:
        """
        Reduces face count using QEM to preserve geometric features.
        """
        import numpy as np
        if len(mesh.faces) <= target_faces:
            return mesh
            
        vertices = [np.array([v.x, v.y, getattr(v, 'z', 0.0)]) for v in mesh.vertices]
        faces = {i: list(face) for i, face in enumerate(mesh.faces)}
        
        # 1. Compute initial quadrics for each vertex
        # Q = sum(p * p^T) where p is the plane [a, b, c, d]
        v_quadrics = [np.zeros((4, 4)) for _ in range(len(vertices))]
        
        # Face planes
        for f_idx, f in faces.items():
            p0, p1, p2 = vertices[f[0]], vertices[f[1]], vertices[f[2]]
            normal = np.cross(p1 - p0, p2 - p0)
            norm = np.linalg.norm(normal)
            if norm < 1e-12: continue
            n = normal / norm
            d = -np.dot(n, p0)
            plane = np.array([n[0], n[1], n[2], d])
            K = np.outer(plane, plane)
            for v_idx in f:
                v_quadrics[v_idx] += K
                
        # Boundary constraints
        # Find boundary edges (shared by exactly 1 face)
        edge_to_faces = defaultdict(list)
        for f_idx, f in faces.items():
            for i in range(3):
                u, v = sorted((f[i], f[(i+1)%3]))
                edge_to_faces[(u, v)].append(f_idx)
                
        boundary_edges = [(u, v, f_list[0]) for (u, v), f_list in edge_to_faces.items() if len(f_list) == 1]
        
        # Add boundary penalty quadrics
        boundary_weight = 1000.0
        for u, v, f_idx in boundary_edges:
            f = faces[f_idx]
            p0, p1, p2 = vertices[f[0]], vertices[f[1]], vertices[f[2]]
            face_normal = np.cross(p1 - p0, p2 - p0)
            if np.linalg.norm(face_normal) < 1e-12: continue
            face_normal = face_normal / np.linalg.norm(face_normal)
            
            edge_vec = vertices[v] - vertices[u]
            if np.linalg.norm(edge_vec) < 1e-12: continue
            edge_dir = edge_vec / np.linalg.norm(edge_vec)
            
            # The constraint plane is perpendicular to both the face and the edge
            bound_normal = np.cross(edge_dir, face_normal)
            bound_normal = bound_normal / np.linalg.norm(bound_normal)
            
            d = -np.dot(bound_normal, vertices[u])
            bound_plane = np.array([bound_normal[0], bound_normal[1], bound_normal[2], d])
            K_bound = np.outer(bound_plane, bound_plane) * boundary_weight
            
            v_quadrics[u] += K_bound
            v_quadrics[v] += K_bound
                
        # 2. Compute cost for each edge
        def get_edge_info(u, v):
            Q = v_quadrics[u] + v_quadrics[v]
            # Find optimal position: solve Q * v_opt = [0, 0, 0, 1]^T
            # Simplified: use midpoint or the better of u, v
            mid = (vertices[u] + vertices[v]) / 2.0
            def error(p):
                p_homog = np.array([p[0], p[1], p[2], 1.0])
                return np.dot(p_homog, np.dot(Q, p_homog))
            
            e_mid = error(mid)
            return e_mid, mid

        v2f = defaultdict(set)
        for f_idx, f in faces.items():
            for v in f: v2f[v].add(f_idx)
            
        edges_heap = []
        edge_set = set()
        for f in faces.values():
            for i in range(3):
                u, v = sorted((f[i], f[(i+1)%3]))
                if (u, v) not in edge_set:
                    edge_set.add((u, v))
                    cost, pos = get_edge_info(u, v)
                    heapq.heappush(edges_heap, (cost, u, v))

        # 3. Iteratively collapse edges
        collapsed_verts = {}
        removed_count = 0
        target_to_remove = len(mesh.faces) - target_faces
        
        while edges_heap and removed_count < target_to_remove:
            cost, u, v = heapq.heappop(edges_heap)
            if u in collapsed_verts or v in collapsed_verts: continue
            
            # Check Link Condition (simplified manifold check)
            common = v2f[u] & v2f[v]
            if len(common) > 2: continue 
            
            # Collapse v into u
            _, new_pos = get_edge_info(u, v)
            vertices[u] = new_pos
            v_quadrics[u] += v_quadrics[v]
            collapsed_verts[v] = u
            
            involved = list(v2f[v])
            for f_idx in involved:
                old_f = faces[f_idx]
                new_f = [u if x == v else x for x in old_f]
                if len(set(new_f)) < 3:
                    # Degenerate
                    for vid in old_f: v2f[vid].discard(f_idx)
                    del faces[f_idx]
                    removed_count += 1
                else:
                    faces[f_idx] = new_f
                    v2f[u].add(f_idx)
                    for vid in new_f: v2f[vid].add(f_idx)
                    
        # 4. Final reconstruction
        final_v = []
        old_to_final = {}
        for i, v in enumerate(vertices):
            if i not in collapsed_verts:
                old_to_final[i] = len(final_v)
                final_v.append(Point3D(v[0], v[1], v[2]))
        
        for old, new in collapsed_verts.items():
            curr = new
            while curr in collapsed_verts: curr = collapsed_verts[curr]
            old_to_final[old] = old_to_final[curr]
            
        final_f = [tuple(old_to_final[i] for i in f) for f in faces.values()]
        return TriangleMesh(final_v, final_f)
