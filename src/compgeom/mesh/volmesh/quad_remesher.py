from __future__ import annotations
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from typing import List, Tuple, Dict, Set
from compgeom.mesh.surfmesh.surface_mesh import SurfaceMesh
from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis

class CrossFieldOptimizer:
    """
    Optimizes a 4-rotationally symmetric (4-RoSy) cross field on a surface.
    Used for field-aligned quad remeshing.
    """
    def __init__(self, mesh: SurfaceMesh):
        self.mesh = mesh
        self.num_faces = len(mesh.faces)
        self.face_normals = np.array(MeshAnalysis.compute_face_normals(mesh))
        
    def estimate_principal_directions(self) -> np.ndarray:
        """
        Estimates principal curvature directions at each face.
        """
        directions = np.zeros((self.num_faces, 3))
        for i in range(self.num_faces):
            n = self.face_normals[i]
            temp = np.array([1, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1, 0])
            u = np.cross(n, temp)
            directions[i] = u / np.linalg.norm(u)
        return directions

    def smooth_field(self, initial_field: np.ndarray, iterations: int = 10) -> np.ndarray:
        """
        Smooths the 4-RoSy field across the surface.
        """
        current_field = initial_field.copy()
        adj = self._build_face_adjacency()
        
        for _ in range(iterations):
            new_field = current_field.copy()
            for i in range(self.num_faces):
                neighbors = adj[i]
                if not neighbors: continue
                
                avg_dir = np.zeros(3)
                ni = self.face_normals[i]
                
                for j in neighbors:
                    nj = self.face_normals[j]
                    vj = current_field[j]
                    
                    vj_transported = vj - np.dot(vj, ni) * ni
                    if np.linalg.norm(vj_transported) < 1e-6: continue
                    vj_transported /= np.linalg.norm(vj_transported)
                    
                    v_cross = np.cross(ni, vj_transported)
                    candidates = [vj_transported, -vj_transported, v_cross, -v_cross]
                    
                    best_cand = candidates[np.argmax([np.dot(c, current_field[i]) for c in candidates])]
                    avg_dir += best_cand
                
                if np.linalg.norm(avg_dir) > 1e-6:
                    new_field[i] = avg_dir / np.linalg.norm(avg_dir)
            current_field = new_field
            
        return current_field

    def _build_face_adjacency(self) -> List[List[int]]:
        edge_to_faces = {}
        for i, face in enumerate(self.mesh.faces):
            for j in range(len(face)):
                v1, v2 = face[j], face[(j+1)%len(face)]
                edge = tuple(sorted((v1, v2)))
                if edge not in edge_to_faces:
                    edge_to_faces[edge] = []
                edge_to_faces[edge].append(i)
        
        adj = [[] for _ in range(self.num_faces)]
        for faces in edge_to_faces.values():
            if len(faces) == 2:
                f1, f2 = faces
                adj[f1].append(f2)
                adj[f2].append(f1)
        return adj

class QuadRemesher:
    """
    Field-aligned quad remeshing placeholder.
    Extracted field-aligned structure can be used for subdivision or parameterization.
    """
    def __init__(self, mesh: SurfaceMesh):
        self.mesh = mesh
        self.optimizer = CrossFieldOptimizer(mesh)
        
    def compute_alignment_field(self) -> np.ndarray:
        """Computes the optimized guidance field."""
        init = self.optimizer.estimate_principal_directions()
        return self.optimizer.smooth_field(init)
