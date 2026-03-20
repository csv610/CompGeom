"""Mesh registration algorithms (Iterative Closest Point)."""
from typing import Tuple

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D

class MeshRegistration:
    """Aligns meshes to each other."""

    @staticmethod
    def icp(source: TriMesh, target: TriMesh, max_iterations: int = 20, tolerance: float = 1e-5) -> Tuple[TriMesh, Tuple]:
        """
        Iterative Closest Point (ICP) algorithm.
        Aligns the source mesh to the target mesh.
        Returns the aligned source mesh and the transformation matrix (4x4).
        """
        try:
            import numpy as np
            from scipy.spatial import cKDTree
        except ImportError:
            raise ImportError("ICP requires 'numpy' and 'scipy'.")

        src_pts = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in source.vertices])
        tgt_pts = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in target.vertices])
        
        # Build KD-Tree for the target points for fast nearest-neighbor lookup
        tree = cKDTree(tgt_pts)
        
        prev_error = float('inf')
        transform = np.eye(4)
        
        for _ in range(max_iterations):
            # 1. Find closest points
            distances, indices = tree.query(src_pts)
            closest_pts = tgt_pts[indices]
            
            # Mean error
            mean_error = np.mean(distances)
            if abs(prev_error - mean_error) < tolerance:
                break
            prev_error = mean_error
            
            # 2. Compute centroids
            centroid_src = np.mean(src_pts, axis=0)
            centroid_tgt = np.mean(closest_pts, axis=0)
            
            # 3. Center the points
            src_centered = src_pts - centroid_src
            tgt_centered = closest_pts - centroid_tgt
            
            # 4. Compute cross-covariance matrix
            H = np.dot(src_centered.T, tgt_centered)
            
            # 5. SVD to find rotation
            U, S, Vt = np.linalg.svd(H)
            R = np.dot(Vt.T, U.T)
            
            # Ensure no reflection (determinant must be 1)
            if np.linalg.det(R) < 0:
                Vt[2, :] *= -1
                R = np.dot(Vt.T, U.T)
                
            # 6. Compute translation
            t = centroid_tgt - np.dot(R, centroid_src)
            
            # 7. Apply transformation to source points
            src_pts = np.dot(src_pts, R.T) + t
            
            # Accumulate transformation
            T_mat = np.eye(4)
            T_mat[:3, :3] = R
            T_mat[:3, 3] = t
            transform = np.dot(T_mat, transform)
            
        new_vertices = [Point3D(p[0], p[1], p[2]) for p in src_pts]
        return TriMesh(new_vertices, source.faces), tuple(map(tuple, transform))
