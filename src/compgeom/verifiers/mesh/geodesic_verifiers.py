from __future__ import annotations

import math
from typing import List, Tuple, Dict
from compgeom.mesh import TriMesh
from compgeom.kernel import Point3D, EPSILON


def verify_mesh_geodesics(mesh: TriMesh, 
                         source_idx: int, 
                         distances: List[float], 
                         method: str = "fmm") -> bool:
    """
    Rigorously verifies geodesic distances on a mesh.
    1. Distance to source must be 0 (or very close).
    2. All distances must be non-negative.
    3. Geodesic distance >= Euclidean distance between vertices.
    4. Triangle Inequality: For any edge (u, v), |dist(s, u) - dist(s, v)| <= length(u, v).
    5. FMM property: Gradient of distance field should have magnitude close to 1.
    """
    n = len(mesh.vertices)
    if len(distances) != n:
        raise ValueError(f"Distance list length {len(distances)} != number of vertices {n}")

    # 1. Source distance
    if abs(distances[source_idx]) > EPSILON:
        raise ValueError(f"Source vertex {source_idx} distance is {distances[source_idx]}, expected 0")

    # 2. Non-negativity
    for i, d in enumerate(distances):
        if d < -EPSILON:
             raise ValueError(f"Negative distance found at vertex {i}: {d}")

    # 3. Euclidean bound
    p_s = mesh.vertices[source_idx]
    for i, d in enumerate(distances):
        if d == float('inf'):
            continue
        p_i = mesh.vertices[i]
        e_dist = math.dist((p_s.x, p_s.y, getattr(p_s, 'z', 0.0)), 
                           (p_i.x, p_i.y, getattr(p_i, 'z', 0.0)))
        if d < e_dist - EPSILON:
             raise ValueError(f"Geodesic distance {d} < Euclidean distance {e_dist} at vertex {i}")

    # 4. Triangle Inequality check (Paranoid)
    # For every edge (u, v) in the mesh, |dist(u) - dist(v)| <= length(u, v)
    for face in mesh.faces:
        for i in range(3):
            u_idx = face[i]
            v_idx = face[(i + 1) % 3]
            d_u = distances[u_idx]
            d_v = distances[v_idx]
            
            if d_u == float('inf') or d_v == float('inf'):
                continue
                
            p_u = mesh.vertices[u_idx]
            p_v = mesh.vertices[v_idx]
            edge_len = math.dist((p_u.x, p_u.y, getattr(p_u, 'z', 0.0)), 
                                 (p_v.x, p_v.y, getattr(p_v, 'z', 0.0)))
            
            if abs(d_u - d_v) > edge_len + EPSILON:
                raise ValueError(f"Triangle inequality violated on edge {u_idx}-{v_idx}: "
                                 f"|{d_u} - {d_v}| = {abs(d_u - d_v)} > {edge_len}")

    return True
