"""Advanced bounding volumes and PCA alignment."""
from typing import Tuple, List

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D

class BoundingVolumes:
    """Calculates Oriented Bounding Boxes (OBB), Minimum Bounding Spheres, and Ellipsoids."""

    @staticmethod
    def compute_obb(mesh: TriMesh) -> Tuple[Point3D, Tuple[Tuple[float, float, float], ...], Tuple[float, float, float]]:
        """
        Computes the Oriented Bounding Box using PCA (Principal Component Analysis).
        Returns: (Center, Axes Matrix 3x3, Extents (half-sizes))
        """
        return BoundingVolumes.compute_obb_points(mesh.vertices)

    @staticmethod
    def compute_obb_points(points: List[Point3D]) -> Tuple[Point3D, Tuple[Tuple[float, float, float], ...], Tuple[float, float, float]]:
        """
        Computes the Oriented Bounding Box using PCA for a set of points.
        Returns: (Center, Axes Matrix 3x3, Extents (half-sizes))
        """
        try:
            import numpy as np
        except ImportError:
            raise ImportError("OBB calculation requires 'numpy'.")

        vertices = np.array([[v.x, v.y, getattr(v, 'z', 0.0)] for v in points])
        
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
    def compute_min_sphere(points: List[Point3D]) -> Tuple[Point3D, float]:
        """
        Computes the Minimum Bounding Sphere using Welzl's algorithm (3D).
        Returns: (Center Point3D, Radius)
        """
        import random
        pts = [(p.x, p.y, getattr(p, 'z', 0.0)) for p in points]
        random.shuffle(pts)
        
        def get_sphere_2pts(p1, p2):
            c = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
            r = math.sqrt(sum((p1[i]-c[i])**2 for i in range(3)))
            return c, r

        def get_sphere_3pts(p1, p2, p3):
            # Triangle circumsphere (minimum sphere containing 3 points)
            a = math.sqrt(sum((p2[i]-p3[i])**2 for i in range(3)))
            b = math.sqrt(sum((p1[i]-p3[i])**2 for i in range(3)))
            c = math.sqrt(sum((p1[i]-p2[i])**2 for i in range(3)))
            
            # Use barycentric coordinates for circumcenter
            a2, b2, c2 = a*a, b*b, c*c
            w1 = a2*(b2+c2-a2)
            w2 = b2*(a2+c2-b2)
            w3 = c2*(a2+b2-c2)
            w_sum = w1 + w2 + w3
            if abs(w_sum) < 1e-12: # Collinear points
                # Use the two furthest points
                d12 = sum((p1[i]-p2[i])**2 for i in range(3))
                d13 = sum((p1[i]-p3[i])**2 for i in range(3))
                d23 = sum((p2[i]-p3[i])**2 for i in range(3))
                if d12 >= d13 and d12 >= d23: return get_sphere_2pts(p1, p2)
                if d13 >= d12 and d13 >= d23: return get_sphere_2pts(p1, p3)
                return get_sphere_2pts(p2, p3)

            center = [(w1*p1[i] + w2*p2[i] + w3*p3[i])/w_sum for i in range(3)]
            radius = math.sqrt(sum((p1[i]-center[i])**2 for i in range(3)))
            return center, radius

        def get_sphere_4pts(p1, p2, p3, p4):
            # Tetrahedron circumsphere
            import numpy as np
            pts = np.array([p1, p2, p3, p4])
            A = np.zeros((3, 3))
            B = np.zeros(3)
            for i in range(3):
                A[i] = 2 * (pts[i+1] - pts[0])
                B[i] = np.sum(pts[i+1]**2) - np.sum(pts[0]**2)
            try:
                center = np.linalg.solve(A, B)
                radius = np.linalg.norm(center - pts[0])
                return tuple(center), radius
            except np.linalg.LinAlgError:
                # Coplanar or degenerate, fallback to 3-point spheres
                best_r = -1
                best_c = None
                for combo in [(p1,p2,p3), (p1,p2,p4), (p1,p3,p4), (p2,p3,p4)]:
                    c, r = get_sphere_3pts(*combo)
                    if r > best_r:
                        # Check if it contains the 4th point
                        p4_other = [p for p in [p1,p2,p3,p4] if p not in combo][0]
                        dist = math.sqrt(sum((p4_other[i]-c[i])**2 for i in range(3)))
                        if dist <= r + 1e-9:
                            best_r, best_c = r, c
                return best_c, best_r

        def min_sphere_with_points(P, R):
            if not P or len(R) == 4:
                if not R: return (0,0,0), 0
                if len(R) == 1: return R[0], 0
                if len(R) == 2: return get_sphere_2pts(R[0], R[1])
                if len(R) == 3: return get_sphere_3pts(R[0], R[1], R[2])
                return get_sphere_4pts(R[0], R[1], R[2], R[3])
            
            p = P.pop()
            c, r = min_sphere_with_points(P, R)
            
            dist = math.sqrt(sum((p[i]-c[i])**2 for i in range(3)))
            if dist <= r + 1e-9:
                P.append(p)
                return c, r
            
            res_c, res_r = min_sphere_with_points(P, R + [p])
            P.append(p)
            return res_c, res_r

        import math
        center, radius = min_sphere_with_points(pts, [])
        return Point3D(*center), radius

    @staticmethod
    def compute_min_ellipse(points: List[Point3D], tolerance: float = 0.01) -> Tuple[Point3D, Tuple[Tuple[float, float, float], ...]]:
        """
        Computes the Minimum Volume Enclosing Ellipsoid (MVEE) using Khachiyan's algorithm.
        Returns: (Center Point3D, (AxisA, AxisB, AxisC)) where axes are vectors defining the ellipsoid.
        The ellipsoid is (x-c)T * A * (x-c) <= 1.
        """
        try:
            import numpy as np
        except ImportError:
            raise ImportError("MVEE calculation requires 'numpy'.")

        P = np.array([[p.x, p.y, getattr(p, 'z', 0.0)] for p in points]).T
        d, n = P.shape
        Q = np.vstack([P, np.ones(n)])
        
        # Initial weights
        u = np.ones(n) / n
        err = 1.0 + tolerance
        
        while err > tolerance:
            # Matrix X = Q * diag(u) * QT
            X = np.dot(Q, np.dot(np.diag(u), Q.T))
            M = np.diag(np.dot(Q.T, np.dot(np.linalg.inv(X), Q)))
            
            j = np.argmax(M)
            step_size = (M[j] - d - 1) / ((d + 1) * (M[j] - 1))
            
            new_u = (1 - step_size) * u
            new_u[j] += step_size
            
            err = np.linalg.norm(new_u - u)
            u = new_u
            
        # Center: c = P * u
        center = np.dot(P, u)
        
        # Matrix A = (1/d) * inv(P * diag(u) * PT - c * cT)
        centered_P = P - center[:, np.newaxis]
        A = np.linalg.inv(np.dot(centered_P, np.dot(np.diag(u), centered_P.T))) / d
        
        # SVD of A to get axes
        U, s, Vh = np.linalg.svd(A)
        # The axes of the ellipsoid are the columns of U divided by sqrt(s)
        axes = []
        for i in range(d):
            axes.append(tuple(U[:, i] / np.sqrt(s[i])))
            
        return Point3D(*center), tuple(axes)

    @staticmethod
    def pca_align(mesh: TriMesh) -> TriMesh:
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
        return TriMesh(new_vertices, mesh.faces)
