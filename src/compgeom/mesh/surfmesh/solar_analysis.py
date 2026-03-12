"""Green Architecture and GIS geometry analysis."""
from typing import List, Tuple
import math

from ..mesh import TriangleMesh
from ...kernel import Point3D

class SolarAnalysis:
    """Provides algorithms for solar potential and urban visibility analysis."""

    @staticmethod
    def sky_view_factor(mesh: TriangleMesh, point: Tuple[float,float,float], samples: int = 100) -> float:
        """
        Calculates the Sky View Factor (SVF) at a specific point on the surface.
        Ratio of visible sky to the entire hemisphere. 
        Critical for urban heat island and solar studies.
        """
        from .mesh_queries import MeshQueries
        
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
        from .mesh_analysis import MeshAnalysis
        from .mesh_queries import MeshQueries
        
        normals = MeshAnalysis.compute_face_normals(mesh)
        radiation = [0.0] * len(mesh.faces)
        
        # Normalize sun direction
        s_mag = math.sqrt(sum(x**2 for x in sun_dir))
        s = (sun_dir[0]/s_mag, sun_dir[1]/s_mag, sun_dir[2]/s_mag)
        
        for i, face in enumerate(mesh.faces):
            # 1. Cosine law (angle of incidence)
            dot = n[0]*s[0] + n[1]*s[1] + n[2]*s[2]
            if dot > 0:
                # 2. Shadow check
                v0 = mesh.vertices[face[0]]
                # Ray origin slightly above surface
                ray_start = (v0.x + n[0]*1e-5, v0.y + n[1]*1e-5, getattr(v0, 'z', 0.0) + n[2]*1e-5)
                if not MeshQueries.ray_intersect(mesh, ray_start, s):
                    radiation[i] = dot
                    
        return radiation
