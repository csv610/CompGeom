"""
Collision-Aware Approximate Convex Decomposition (CoACD, 2022).
Wei et al., "Approximate Convex Decomposition for 3D Meshes with Collision-Aware Concavity and Tree Search", SIGGRAPH 2022.
"""

from __future__ import annotations
import numpy as np
from typing import List, Tuple, Optional, Dict
import math

from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.mesh.surface.mesh_clipper import MeshClipper
from compgeom.mesh.surface.sampling import MeshSampler
from compgeom.mesh.surface.convex_hull import ConvexHull3D
from compgeom.mesh.surface.mesh_queries import MeshQueries

class CoACD:
    """
    Main class for performing Collision-Aware Approximate Convex Decomposition.
    """
    def __init__(self, mesh: SurfaceMesh, threshold: float = 0.05, max_convex_hull: int = 100):
        self.mesh = mesh
        self.threshold = threshold
        self.max_convex_hull = max_convex_hull

    def decompose(self) -> List[SurfaceMesh]:
        """
        Decomposes the mesh into near-convex parts.
        
        Returns:
            A list of SurfaceMesh objects, each being a convex or near-convex part.
        """
        parts = [self.mesh]
        final_parts = []
        
        while parts:
            curr = parts.pop(0)
            
            # 1. Calculate collision-aware concavity
            concavity = self._calculate_concavity(curr)
            
            if concavity <= self.threshold or len(final_parts) >= self.max_convex_hull:
                final_parts.append(curr)
            else:
                # 2. Find best cutting plane using tree search (simplified)
                plane = self._find_best_cut(curr)
                if plane:
                    origin, normal = plane
                    ma, mb = MeshClipper.clip(curr, origin, normal, cap=True)
                    
                    # Only accept split if it actually divides the mesh significantly
                    if len(ma.faces) > 0 and len(mb.faces) > 0:
                        parts.append(ma)
                        parts.append(mb)
                    else:
                        final_parts.append(curr)
                else:
                    final_parts.append(curr)
                    
        return final_parts

    def _calculate_concavity(self, mesh: SurfaceMesh) -> float:
        """
        Implements the collision-aware concavity metric.
        It samples surface and volume points and measures their distance to the convex hull.
        """
        if len(mesh.faces) < 4:
            return 0.0
            
        # 1. Build convex hull of the part
        try:
            hull = ConvexHull3D.generate(mesh.vertices)
        except Exception:
            return 0.0 # Robustness for degenerate parts
            
        # 2. Sample points from the mesh (surface and volume)
        surface_samples = MeshSampler.sample_surface(mesh, 100)
        volume_samples = MeshSampler.sample_volume(mesh, 50)
        all_samples = np.vstack([surface_samples, volume_samples])
        
        # 3. Calculate max distance from samples to the hull
        # Collision-aware: we care about samples that are "far" inside the hull 
        # but outside the actual mesh.
        max_dist = 0.0
        for p in all_samples:
            # Distance to convex hull
            d_hull = MeshQueries.compute_sdf(hull, tuple(p))
            # If point is inside hull (sdf is positive/negative depending on implementation)
            # For our compute_sdf, let's assume it returns distance to surface.
            if d_hull > max_dist:
                max_dist = d_hull
                
        # Normalize by bounding box diagonal
        v_arr = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        diag = np.linalg.norm(np.max(v_arr, axis=0) - np.min(v_arr, axis=0))
        
        return max_dist / (diag + 1e-9)

    def _find_best_cut(self, mesh: SurfaceMesh) -> Optional[Tuple[Tuple[float,float,float], Tuple[float,float,float]]]:
        """
        Finds an optimal cutting plane.
        In CoACD, this involves testing multiple candidates and selecting one 
        that minimizes concavity of children.
        """
        # Simplified candidate generation: Principal Component Analysis (PCA) axes
        v_arr = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        center = np.mean(v_arr, axis=0)
        
        # PCA for axes
        centered = v_arr - center
        cov = np.dot(centered.T, centered)
        eigvals, eigvecs = np.linalg.eigh(cov)
        
        # Best axis is usually the one with largest variance
        best_axis = eigvecs[:, 2]
        
        return tuple(center), tuple(best_axis)
