"""AABB Tree for fast spatial queries (Ray intersection, nearest point)."""
from __future__ import annotations
import math
from typing import List, Tuple, Optional, Union

from ..mesh import TriangleMesh
from ...kernel import Point3D

class AABBNode:
    def __init__(self, faces: List[int], bmin: Tuple[float, float, float], bmax: Tuple[float, float, float]):
        self.faces = faces
        self.bmin = bmin
        self.bmax = bmax
        self.left: Optional[AABBNode] = None
        self.right: Optional[AABBNode] = None

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

class AABBTree:
    """Bounding Volume Hierarchy (AABB Tree) for accelerating mesh queries."""

    def __init__(self, mesh: TriangleMesh, max_faces_per_leaf: int = 10):
        self.mesh = mesh
        self.faces = mesh.faces
        self.vertices = mesh.vertices
        
        # Precompute face AABBs and centroids
        self.face_aabbs = []
        self.face_centroids = []
        for face in self.faces:
            v0, v1, v2 = [self.vertices[idx] for idx in face]
            pts = [(v0.x, v0.y, getattr(v0, 'z', 0.0)),
                   (v1.x, v1.y, getattr(v1, 'z', 0.0)),
                   (v2.x, v2.y, getattr(v2, 'z', 0.0))]
            
            fmin = (min(p[0] for p in pts), min(p[1] for p in pts), min(p[2] for p in pts))
            fmax = (max(p[0] for p in pts), max(p[1] for p in pts), max(p[2] for p in pts))
            centroid = ((fmin[0] + fmax[0])/2, (fmin[1] + fmax[1])/2, (fmin[2] + fmax[2])/2)
            
            self.face_aabbs.append((fmin, fmax))
            self.face_centroids.append(centroid)
            
        self.root = self._build(list(range(len(self.faces))), 0, max_faces_per_leaf)

    def _build(self, face_indices: List[int], depth: int, max_leaf: int) -> AABBNode:
        if not face_indices:
            return None
            
        # Compute bounding box for this set of faces
        bmin = [float('inf')] * 3
        bmax = [float('-inf')] * 3
        for idx in face_indices:
            fmin, fmax = self.face_aabbs[idx]
            for i in range(3):
                bmin[i] = min(bmin[i], fmin[i])
                bmax[i] = max(bmax[i], fmax[i])
        
        node = AABBNode(face_indices, tuple(bmin), tuple(bmax))
        
        if len(face_indices) <= max_leaf:
            return node
            
        # Split along the largest axis
        axis = 0
        extent = [bmax[i] - bmin[i] for i in range(3)]
        if extent[1] > extent[0] and extent[1] > extent[2]: axis = 1
        elif extent[2] > extent[0]: axis = 2
        
        # Sort faces by centroid along the axis
        face_indices.sort(key=lambda idx: self.face_centroids[idx][axis])
        mid = len(face_indices) // 2
        
        node.left = self._build(face_indices[:mid], depth + 1, max_leaf)
        node.right = self._build(face_indices[mid:], depth + 1, max_leaf)
        node.faces = [] # Clear non-leaf face lists
        
        return node

    def ray_intersect(self, origin: Tuple[float, float, float], direction: Tuple[float, float, float]) -> List[Tuple[int, float]]:
        """Fast ray-mesh intersection using the AABB Tree."""
        intersections = []
        self._intersect_recursive(self.root, origin, direction, intersections)
        intersections.sort(key=lambda x: x[1])
        return intersections

    def _intersect_recursive(self, node: AABBNode, origin: Tuple[float, float, float], 
                             direction: Tuple[float, float, float], results: List[Tuple[int, float]]):
        if not node or not self._ray_aabb_intersect(node.bmin, node.bmax, origin, direction):
            return
            
        if node.is_leaf():
            from .mesh_queries import MeshQueries
            # Use brute-force checker for the few faces in leaf
            for f_idx in node.faces:
                res = MeshQueries._single_ray_tri_intersect(self.mesh, f_idx, origin, direction)
                if res is not None:
                    results.append((f_idx, res))
        else:
            self._intersect_recursive(node.left, origin, direction, results)
            self._intersect_recursive(node.right, origin, direction, results)

    def _ray_aabb_intersect(self, bmin: Tuple[float, float, float], bmax: Tuple[float, float, float], 
                            origin: Tuple[float, float, float], direction: Tuple[float, float, float]) -> bool:
        tmin, tmax = float('-inf'), float('inf')
        for i in range(3):
            if abs(direction[i]) < 1e-9:
                if origin[i] < bmin[i] or origin[i] > bmax[i]:
                    return False
            else:
                inv_d = 1.0 / direction[i]
                t1 = (bmin[i] - origin[i]) * inv_d
                t2 = (bmax[i] - origin[i]) * inv_d
                tmin = max(tmin, min(t1, t2))
                tmax = min(tmax, max(t1, t2))
                
        return tmax >= max(0.0, tmin)
