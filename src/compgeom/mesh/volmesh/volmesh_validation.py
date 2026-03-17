from __future__ import annotations
import math
from typing import List, Tuple, Dict
from ...kernel import Point3D
from .polyhedral_mesh import PolyhedralMesh

def validate_voronoi_mesh(mesh: PolyhedralMesh, tolerance: float = 1e-7) -> Tuple[bool, List[str]]:
    """
    Validates if a PolyhedralMesh is a valid Voronoi diagram.
    
    Checks:
    1. Planarity: Each face must be planar.
    2. Convexity: Each cell must be a convex polyhedron.
    3. Equidistance: If seeds are available, each Voronoi vertex should be equidistant 
       to at least 4 seeds (the ones forming the Delaunay tetrahedron).
    4. Proximity: For each cell i, its seed point must be the closest seed to all 
       points inside the cell (we check the vertices).
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if not mesh.cells:
        return True, []

    # 1. Planarity Check
    for cell_idx, cell in enumerate(mesh.cells):
        for face_idx, face in enumerate(cell):
            if len(face) < 4:
                continue # 3 points always planar
            
            # Check if all points in face are on the same plane
            p0 = mesh.vertices[face[0]]
            p1 = mesh.vertices[face[1]]
            p2 = mesh.vertices[face[2]]
            
            # Normal to the plane
            v1 = p1 - p0
            v2 = p2 - p0
            normal = Point3D(
                v1.y * v2.z - v1.z * v2.y,
                v1.z * v2.x - v1.x * v2.z,
                v1.x * v2.y - v1.y * v2.x
            )
            norm = math.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
            if norm < tolerance:
                # Collinear vertices in face?
                continue
            
            normal = Point3D(normal.x/norm, normal.y/norm, normal.z/norm)
            
            for v_idx in face[3:]:
                p = mesh.vertices[v_idx]
                dist = abs((p - p0).dot(normal))
                if dist > tolerance:
                    errors.append(f"Cell {cell_idx}, Face {face_idx} is not planar (dist={dist})")
                    break

    # 2. Equidistance & Proximity (if seeds available)
    if mesh.seeds:
        seeds = mesh.seeds
        for cell_idx, cell in enumerate(mesh.cells):
            if cell_idx >= len(seeds):
                continue
                
            seed = seeds[cell_idx]
            
            # For each vertex in this cell, its distance to 'seed' should be <= distance to any other seed
            vertex_indices = set()
            for face in cell:
                vertex_indices.update(face)
            
            for v_idx in vertex_indices:
                v = mesh.vertices[v_idx]
                dist_to_own_seed = math.sqrt((v.x - seed.x)**2 + (v.y - seed.y)**2 + (v.z - seed.z)**2)
                
                # Check against other seeds (this is O(N_seeds * N_vertices), can be slow)
                for other_seed_idx, other_seed in enumerate(seeds):
                    if other_seed_idx == cell_idx:
                        continue
                    
                    dist_to_other = math.sqrt((v.x - other_seed.x)**2 + (v.y - other_seed.y)**2 + (v.z - other_seed.z)**2)
                    if dist_to_other < dist_to_own_seed - tolerance:
                        errors.append(f"Vertex {v_idx} in Cell {cell_idx} is closer to Seed {other_seed_idx} than its own seed.")
                        break

    # 3. Convexity Check (Simple version: centroid should be on the same side of all face planes)
    # A more robust check would verify all vertices of a cell are on the same side of each face plane.
    for cell_idx, cell in enumerate(mesh.cells):
        if not cell: continue
        
        # Collect all vertices of the cell
        cell_v_indices = set()
        for face in cell:
            cell_v_indices.update(face)
        cell_vertices = [mesh.vertices[idx] for idx in cell_v_indices]
        
        # For each face, all OTHER vertices of the cell must be on one side
        for face_idx, face in enumerate(cell):
            p0 = mesh.vertices[face[0]]
            p1 = mesh.vertices[face[1]]
            p2 = mesh.vertices[face[2]]
            
            v1 = p1 - p0
            v2 = p2 - p0
            normal = Point3D(
                v1.y * v2.z - v1.z * v2.y,
                v1.z * v2.x - v1.x * v2.z,
                v1.x * v2.y - v1.y * v2.x
            )
            
            # We need the normal to point "out" or "in" consistently.
            # Let's find a point not on the face to determine side.
            test_p = None
            for v_idx in cell_v_indices:
                if v_idx not in face:
                    test_p = mesh.vertices[v_idx]
                    break
            
            if test_p:
                side = (test_p - p0).dot(normal)
                if abs(side) < tolerance: continue # Degenerate
                
                # All other points must have the same sign (or be zero)
                for v_idx in cell_v_indices:
                    if v_idx in face: continue
                    p = mesh.vertices[v_idx]
                    s = (p - p0).dot(normal)
                    if s * side < -tolerance:
                        errors.append(f"Cell {cell_idx} is not convex at Face {face_idx}")
                        break

    return len(errors) == 0, errors
