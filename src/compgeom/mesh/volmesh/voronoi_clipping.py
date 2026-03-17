from __future__ import annotations
import math
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict

from ...kernel import Point3D, Plane
from ...kernel.math_utils import EPSILON

def clip_polyhedron_by_plane(vertices: List[Point3D], 
                              faces: List[List[int]], 
                              plane: Plane) -> Tuple[List[Point3D], List[List[int]]]:
    """
    Clips a convex polyhedron by a plane. 
    Keeps the part in the half-space where plane.signed_distance(p) >= 0.
    """
    # 1. Classify vertices
    v_sides = [plane.signed_distance(v) for v in vertices]
    
    # If all points are on the positive side, return as is
    if all(s >= -EPSILON for s in v_sides):
        return vertices, faces
    
    # If all points are on the negative side, return empty
    if all(s <= EPSILON for s in v_sides):
        return [], []

    new_vertices = list(vertices)
    # Map from edge (v1, v2) to new vertex index on the plane
    edge_intersections = {}

    def get_intersection(v1_idx, v2_idx):
        edge = tuple(sorted((v1_idx, v2_idx)))
        if edge in edge_intersections:
            return edge_intersections[edge]
        
        p1, p2 = vertices[v1_idx], vertices[v2_idx]
        d1, d2 = v_sides[v1_idx], v_sides[v2_idx]
        
        # t = d1 / (d1 - d2)
        t = d1 / (d1 - d2)
        new_v = p1 + (p2 - p1) * t
        
        new_idx = len(new_vertices)
        new_vertices.append(new_v)
        edge_intersections[edge] = new_idx
        return new_idx

    new_faces = []
    points_on_plane = [] # Indices of vertices that are new or exactly on plane

    for face in faces:
        new_face = []
        for i in range(len(face)):
            v1_idx = face[i]
            v2_idx = face[(i + 1) % len(face)]
            
            s1, s2 = v_sides[v1_idx], v_sides[v2_idx]
            
            if s1 >= -EPSILON:
                new_face.append(v1_idx)
            
            # Check for intersection
            if (s1 > EPSILON and s2 < -EPSILON) or (s1 < -EPSILON and s2 > EPSILON):
                inter_idx = get_intersection(v1_idx, v2_idx)
                new_face.append(inter_idx)
                points_on_plane.append(inter_idx)
        
        if len(new_face) >= 3:
            new_faces.append(new_face)

    # Now we need to add a new face for the points on the plane
    if points_on_plane:
        # Order the points on the plane to form a convex polygon
        # Since the polyhedron is convex, the intersection with a plane is a convex polygon.
        unique_points_on_plane = sorted(list(set(points_on_plane)))
        if len(unique_points_on_plane) >= 3:
            # Simple way to order: project to plane and sort by angle
            ordered_face = _order_points_on_plane(unique_points_on_plane, new_vertices, plane)
            if ordered_face:
                new_faces.append(ordered_face)

    # Clean up: remove unused vertices and re-index
    return _cleanup_mesh(new_vertices, new_faces, v_sides)

def _order_points_on_plane(indices: List[int], vertices: List[Point3D], plane: Plane) -> List[int]:
    if not indices: return []
    
    # Project 3D points to 2D on the plane
    # 1. Find a coordinate system on the plane
    n = plane.normal
    if abs(n.x) < 0.9:
        u = Point3D(1, 0, 0).cross(n)
    else:
        u = Point3D(0, 1, 0).cross(n)
    u = u / math.sqrt(u.x**2 + u.y**2 + u.z**2)
    v = n.cross(u)
    
    pts = [vertices[i] for i in indices]
    p0 = pts[0]
    
    # 2D coords relative to centroid
    centroid = Point3D(sum(p.x for p in pts)/len(pts), sum(p.y for p in pts)/len(pts), sum(p.z for p in pts)/len(pts))
    
    def get_angle(p):
        rel = p - centroid
        return math.atan2(rel.dot(v), rel.dot(u))

    sorted_indices = sorted(indices, key=lambda idx: get_angle(vertices[idx]))
    return sorted_indices

def _cleanup_mesh(vertices: List[Point3D], faces: List[List[int]], v_sides: List[float]) -> Tuple[List[Point3D], List[List[int]]]:
    used_v = set()
    for face in faces:
        used_v.update(face)
    
    new_v_list = []
    old_to_new = {}
    for i, v in enumerate(vertices):
        if i in used_v:
            old_to_new[i] = len(new_v_list)
            new_v_list.append(v)
            
    new_faces = [[old_to_new[idx] for idx in face] for face in faces]
    return new_v_list, new_faces
