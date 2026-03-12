"""Mesh decimation using edge collapses."""
from __future__ import annotations
import heapq
from collections import defaultdict
from typing import List, Tuple, Dict, Set

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MeshDecimator:
    """Simplifies triangle meshes by iteratively collapsing edges."""

    @staticmethod
    def decimate(mesh: TriangleMesh, target_faces: int) -> TriangleMesh:
        """
        Reduces face count by collapsing shortest edges.
        Ensures mesh remains manifold during collapse.
        """
        if len(mesh.faces) <= target_faces:
            return mesh
            
        vertices = list(mesh.vertices)
        # Using dict to track active faces as tuples
        faces = {i: face for i, face in enumerate(mesh.faces)}
        
        # Build connectivity
        v2f = defaultdict(set)
        for f_idx, face in faces.items():
            for v in face:
                v2f[v].add(f_idx)
                
        def get_edge_key(u, v):
            return tuple(sorted((u, v)))
            
        def get_dist_sq(u, v):
            p1, p2 = vertices[u], vertices[v]
            return (p1.x-p2.x)**2 + (p1.y-p2.y)**2 + (getattr(p1, 'z', 0.0)-getattr(p2, 'z', 0.0))**2

        # Priority queue of edges
        edges_heap = []
        all_edges = set()
        for face in faces.values():
            for i in range(3):
                edge = get_edge_key(face[i], face[(i+1)%3])
                if edge not in all_edges:
                    all_edges.add(edge)
                    heapq.heappush(edges_heap, (get_dist_sq(*edge), edge))

        faces_to_remove = len(mesh.faces) - target_faces
        removed_faces_count = 0
        
        collapsed_verts = {} # maps old_idx to new_idx

        while edges_heap and removed_faces_count < faces_to_remove:
            cost, (u, v) = heapq.heappop(edges_heap)
            
            # Check if vertices still exist and aren't already collapsed
            if u in collapsed_verts or v in collapsed_verts:
                continue
                
            # Manifold preservation: Link condition (Simplified)
            # Both vertices must share exactly 2 common neighbors (for interior edges)
            common_neighbors = set()
            for f_idx in v2f[u]:
                common_neighbors.update(faces[f_idx])
            neighbor_v = set()
            for f_idx in v2f[v]:
                neighbor_v.update(faces[f_idx])
            common_neighbors &= neighbor_v
            common_neighbors.discard(u)
            common_neighbors.discard(v)
            
            if len(common_neighbors) > 2:
                continue # Skip to avoid non-manifold
                
            # Perform collapse: Move u to midpoint, remove v
            p1, p2 = vertices[u], vertices[v]
            new_pt = Point3D((p1.x+p2.x)/2, (p1.y+p2.y)/2, (getattr(p1, 'z', 0.0)+getattr(p2, 'z', 0.0))/2)
            vertices[u] = new_pt
            collapsed_verts[v] = u
            
            # Update faces sharing v to share u
            involved_faces = list(v2f[v])
            for f_idx in involved_faces:
                old_face = faces[f_idx]
                new_face = tuple(u if x == v else x for x in old_face)
                
                if len(set(new_face)) < 3:
                    # Degenerate face (edge we just collapsed)
                    for vertex in old_face:
                        v2f[vertex].discard(f_idx)
                    del faces[f_idx]
                    removed_faces_count += 1
                else:
                    faces[f_idx] = new_face
                    v2f[u].add(f_idx)
                    for vertex in old_face:
                        if vertex != v:
                            v2f[vertex].add(f_idx)
            
            # Update edges heap for neighbors of u? (Skipped for performance in this simple version)

        # Rebuild final mesh
        final_vertices = []
        old_to_final = {}
        for i, v in enumerate(vertices):
            if i not in collapsed_verts:
                old_to_final[i] = len(final_vertices)
                final_vertices.append(v)
        
        # Resolve collapsed mapping
        for old, new in collapsed_verts.items():
            curr = new
            while curr in collapsed_verts:
                curr = collapsed_verts[curr]
            old_to_final[old] = old_to_final[curr]
            
        final_faces = []
        for face in faces.values():
            final_faces.append(tuple(old_to_final[idx] for idx in face))
            
        return TriangleMesh(final_vertices, final_faces)
