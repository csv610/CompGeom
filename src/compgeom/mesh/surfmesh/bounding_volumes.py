"""Advanced bounding volumes and PCA alignment."""
from typing import Tuple, List

from ..mesh import TriangleMesh
from ...kernel import Point3D

class BoundingVolumes:
    """Calculates Oriented Bounding Boxes (OBB) and PCA alignment."""

    @staticmethod
    def compute_obb(mesh: TriangleMesh) -> Tuple[Point3D, Tuple[Tuple[float, float, float], ...], Tuple[float, float, float]]:
        """
        Computes the Oriented Bounding Box using PCA (Principal Component Analysis).
        Returns: (Center, Axes Matrix 3x3, Extents (half-sizes))
        """
        try:
            import numpy as np
        except ImportError:
            raise ImportError("OBB calculation requires 'numpy'.")

        vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        
        # Calculate covariance matrix
        centroid = np.mean(vertices, axis=0)
        centered_vertices = vertices - centroid
        covariance = np.cov(centered_vertices, rowvar=False)
        
        # Eigen decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        
        # Sort eigenvectors by eigenvalues descending
        idx = eigenvalues.argsort()[::-1]
        eigenvectors = eigenvectors[:, idx]
        
        # Project vertices onto the new basis to find extents
        projected = np.dot(centered_vertices, eigenvectors)
        
        min_proj = np.min(projected, axis=0)
        max_proj = np.max(projected, axis=0)
        
        # OBB Center in global space
        center_proj = (max_proj + min_proj) / 2.0
        center = centroid + np.dot(eigenvectors, center_proj)
        
        # Half extents
        extents = (max_proj - min_proj) / 2.0
        
        # Ensure right-handed coordinate system
        if np.linalg.det(eigenvectors) < 0:
            eigenvectors[:, 2] = -eigenvectors[:, 2]
            
        axes = (
            tuple(eigenvectors[:, 0]),
            tuple(eigenvectors[:, 1]),
            tuple(eigenvectors[:, 2])
        )
        
        return Point3D(*center), axes, tuple(extents)

    @staticmethod
    def pca_align(mesh: TriangleMesh) -> TriangleMesh:
        """
        Aligns the mesh to the world axes based on its Principal Components.
        Translates centroid to origin and rotates so its longest axis is X, etc.
        """
        try:
            import numpy as np
        except ImportError:
            raise ImportError("PCA alignment requires 'numpy'.")

        vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in mesh.vertices])
        centroid = np.mean(vertices, axis=0)
        centered = vertices - centroid
        
        covariance = np.cov(centered, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        
        idx = eigenvalues.argsort()[::-1]
        eigenvectors = eigenvectors[:, idx]
        
        if np.linalg.det(eigenvectors) < 0:
            eigenvectors[:, 2] = -eigenvectors[:, 2]
            
        # The inverse of the rotation matrix is its transpose
        aligned = np.dot(centered, eigenvectors)
        
        new_vertices = [Point3D(p[0], p[1], p[2]) for p in aligned]
        return TriangleMesh(new_vertices, mesh.faces)
