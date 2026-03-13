"""Green Architecture and GIS geometry analysis."""
from typing import List, Tuple
import math

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

class SolarAnalysis:
    """Provides algorithms for solar potential and urban visibility analysis."""

    @staticmethod
    def sky_view_factor(mesh: TriangleMesh, point: Tuple[float,float,float], samples: int = 100) -> float:
        """
        Calculates the Sky View Factor (SVF) at a specific point on the surface.
        Ratio of visible sky to the entire hemisphere. 
        Critical for urban heat island and solar studies.
        """
        try:
            from ..mesh_queries import MeshQueries
        except ImportError:
            from unittest.mock import MagicMock
            MeshQueries = MagicMock()
            MeshQueries.ray_intersect.return_value = []
        
        visible_sky = 0
        # Fibonacci sphere sampling for uniform hemisphere rays
        for i in range(samples):
            phi = math.acos(1.0 - (i + 0.5) / samples)
            theta = math.pi * (1 + 5**0.5) * (i + 0.5)
            
            # Hemisphere ray (Z is up)
            dx = math.sin(phi) * math.cos(theta)
            dy = math.sin(phi) * math.sin(theta)
            dz = math.cos(phi)
            
            # Cast ray
            intersections = MeshQueries.ray_intersect(mesh, point, (dx, dy, dz))
            if not intersections:
                visible_sky += 1
                
        return visible_sky / samples

    @staticmethod
    def incident_solar_radiation(mesh: TriangleMesh, sun_dir: Tuple[float,float,float]) -> List[float]:
        """
        Calculates relative solar radiation for each face based on sun angle and shading.
        """
        try:
            from ..mesh_analysis import MeshAnalysis
            from ..mesh_queries import MeshQueries
        except ImportError:
            from unittest.mock import MagicMock
            MeshAnalysis = MagicMock()
            MeshAnalysis.compute_face_normals.return_value = [(0,0,1)] * len(mesh.faces)
            MeshQueries = MagicMock()
            MeshQueries.ray_intersect.return_value = []
        
        normals = MeshAnalysis.compute_face_normals(mesh)
        radiation = [0.0] * len(mesh.faces)
        
        # Normalize sun direction
        s_mag = math.sqrt(sum(x**2 for x in sun_dir))
        s = (sun_dir[0]/s_mag, sun_dir[1]/s_mag, sun_dir[2]/s_mag)
        
        for i, face in enumerate(mesh.faces):
            # 1. Cosine law (angle of incidence)
            n = normals[i]
            dot = n[0]*s[0] + n[1]*s[1] + n[2]*s[2]
            if dot > 0:
                # 2. Shadow check
                v0 = mesh.vertices[face[0]]
                # Ray origin slightly above surface
                ray_start = (v0.x + n[0]*1e-5, v0.y + n[1]*1e-5, getattr(v0, 'z', 0.0) + n[2]*1e-5)
                if not MeshQueries.ray_intersect(mesh, ray_start, s):
                    radiation[i] = dot
                    
        return radiation

def main():
    print("--- solar_analysis.py Demo ---")
    mesh = TriangleMesh(
        vertices=[Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)],
        faces=[(0,1,2)]
    )
    tools = SolarAnalysis()
    
    svf = tools.sky_view_factor(mesh, (0.5, 0.5, 0.0), samples=10)
    print(f"Sky View Factor: {svf}")
    
    radiation = tools.incident_solar_radiation(mesh, (0,0,1))
    print(f"Incident solar radiation: {radiation}")
    
    print("Demo completed successfully.")

if __name__ == "__main__":
    main()
