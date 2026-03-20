"""Riemannian patch identification for surface meshes."""
from collections import defaultdict
import math
from typing import List, Union, Tuple

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.quadmesh.quadmesh import QuadMesh
from compgeom.mesh.surface.polygon.polygon import PolygonMesh

def _compute_face_normal(vertices, face_v_indices) -> Tuple[float, float, float]:
    """Helper to compute a face normal."""
    v_indices = face_v_indices
    v0 = vertices[v_indices[0]]
    v1 = vertices[v_indices[1]]
    v2 = vertices[v_indices[2]]
    
    p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
    p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
    p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
    
    ux, uy, uz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
    vx, vy, vz = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
    
    nx = uy*vz - uz*vy
    ny = uz*vx - ux*vz
    nz = ux*vy - uy*vx
    
    length = math.sqrt(nx*nx + ny*ny + nz*nz)
    if length > 1e-9:
        return (nx/length, ny/length, nz/length)
    return (0.0, 0.0, 0.0)

def identify_riemannian_patches(mesh: Union[TriMesh, QuadMesh, PolygonMesh], angle_threshold_deg: float = 30.0) -> List[Union[TriMesh, QuadMesh, PolygonMesh]]:
    """
    Identifies Riemannian patches of a surface mesh.
    Patches are defined as connected components where adjacent faces have 
    normals that differ by less than angle_threshold_deg.
    
    For a cube, with a threshold < 90 deg, this will return 6 patches.
    """
    threshold_cos = math.cos(math.radians(angle_threshold_deg))
    
    # 1. Compute all face normals
    face_normals = []
    vertices = [n.point for n in mesh.nodes] if hasattr(mesh, 'nodes') else mesh.vertices
    for face_obj in mesh.faces:
        face_v_indices = getattr(face_obj, 'v_indices', face_obj)
        face_normals.append(_compute_face_normal(vertices, face_v_indices))
        
    # 2. Build adjacency list for faces sharing edges AND having similar normals
    edge_to_faces = defaultdict(list)
    for i, face_obj in enumerate(mesh.faces):
        face = getattr(face_obj, 'v_indices', face_obj)
        n = len(face)
        for j in range(n):
            u = face[j]
            v = face[(j + 1) % n]
            edge = tuple(sorted((u, v)))
            edge_to_faces[edge].append(i)
            
    face_adjacency = defaultdict(list)
    for faces in edge_to_faces.values():
        if len(faces) >= 2:
            for i in range(len(faces)):
                for j in range(i + 1, len(faces)):
                    f1_idx, f2_idx = faces[i], faces[j]
                    n1 = face_normals[f1_idx]
                    n2 = face_normals[f2_idx]
                    
                    # Dot product of normals
                    dot = n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2]
                    
                    if dot >= threshold_cos:
                        face_adjacency[f1_idx].append(f2_idx)
                        face_adjacency[f2_idx].append(f1_idx)

    # 3. BFS to find connected components
    visited_faces = set()
    patches = []
    mesh_type = type(mesh)
    
    for i in range(len(mesh.faces)):
        if i in visited_faces:
            continue
            
        component_faces_indices = []
        queue = [i]
        visited_faces.add(i)
        
        while queue:
            curr = queue.pop(0)
            component_faces_indices.append(curr)
            
            for neighbor in face_adjacency.get(curr, []):
                if neighbor not in visited_faces:
                    visited_faces.add(neighbor)
                    queue.append(neighbor)
                    
        # 4. Extract sub-mesh
        patch_faces_objs = [mesh.faces[idx] for idx in component_faces_indices]
        old_to_new = {}
        new_vertices = []
        new_faces = []
        
        for face_obj in patch_faces_objs:
            face_v_indices = getattr(face_obj, 'v_indices', face_obj)
            new_face_v = []
            for v_idx in face_v_indices:
                if v_idx not in old_to_new:
                    old_to_new[v_idx] = len(new_vertices)
                    if hasattr(mesh, 'nodes'):
                        new_vertices.append(mesh.nodes[v_idx].point)
                    else:
                        new_vertices.append(mesh.vertices[v_idx])
                new_face_v.append(old_to_new[v_idx])
            new_faces.append(tuple(new_face_v))
            
        patches.append(mesh_type(new_vertices, new_faces))
        
    return patches
