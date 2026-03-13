"""Metrology and Quality Control algorithms."""
import random
import math
from typing import List, Tuple, Optional

try:
    from ..mesh import TriangleMesh
    from ...kernel import Point3D
except ImportError:
    class TriangleMesh:
        def __init__(self, vertices=None, faces=None):
            self.vertices = vertices or []
            self.faces = faces or []
    class Point3D:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x = x
            self.y = y
            self.z = z

class MetrologyTools:
    """Provides algorithms for industrial inspection and primitive fitting."""

    @staticmethod
    def fit_plane_ransac(points: List[Point3D], iterations: int = 100, threshold: float = 0.01) -> Tuple[Tuple[float, float, float, float], List[int]]:
        """
        Fits a plane (ax + by + cz + d = 0) to a noisy point cloud using RANSAC.
        Returns the plane coefficients and indices of inlier points.
        """
        best_plane = (0, 0, 0, 0)
        best_inliers = []
        
        num_pts = len(points)
        if num_pts < 3: return best_plane, []
        
        for _ in range(iterations):
            # 1. Pick 3 random points
            sample = random.sample(range(num_pts), 3)
            p1, p2, p3 = points[sample[0]], points[sample[1]], points[sample[2]]
            
            # 2. Calculate plane normal
            v1 = (p2.x-p1.x, p2.y-p1.y, getattr(p2, 'z', 0.0)-getattr(p1, 'z', 0.0))
            v2 = (p3.x-p1.x, p3.y-p1.y, getattr(p3, 'z', 0.0)-getattr(p1, 'z', 0.0))
            
            nx = v1[1]*v2[2] - v1[2]*v2[1]
            ny = v1[2]*v2[0] - v1[0]*v2[2]
            nz = v1[0]*v2[1] - v1[1]*v2[0]
            
            mag = math.sqrt(nx*nx + ny*ny + nz*nz)
            if mag < 1e-9: continue
            nx, ny, nz = nx/mag, ny/mag, nz/mag
            d = -(nx*p1.x + ny*p1.y + nz*getattr(p1, 'z', 0.0))
            
            # 3. Count inliers
            current_inliers = []
            for i, p in enumerate(points):
                dist = abs(nx*p.x + ny*p.y + nz*getattr(p, 'z', 0.0) + d)
                if dist < threshold:
                    current_inliers.append(i)
                    
            if len(current_inliers) > len(best_inliers):
                best_inliers = current_inliers
                best_plane = (nx, ny, nz, d)
                
        return best_plane, best_inliers

def main():
    print("--- metrology_tools.py Demo ---")
    points = [
        Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0), Point3D(0.5,0.5,0),
        Point3D(2,2,10) # Outlier
    ]
    tools = MetrologyTools()
    plane, inliers = tools.fit_plane_ransac(points)
    print(f"Fitted plane: {plane}")
    print(f"Number of inliers: {len(inliers)}")
    
    print("Demo completed successfully.")

if __name__ == "__main__":
    main()
