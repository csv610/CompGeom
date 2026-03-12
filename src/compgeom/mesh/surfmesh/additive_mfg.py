"""Additive Manufacturing (3D Printing) geometry algorithms."""
import math
from typing import List, Tuple

from ..mesh import TriangleMesh
from ...kernel import Point3D

class AdditiveMfg:
    """Provides algorithms for 3D printing analysis and support generation."""

    @staticmethod
    def detect_overhangs(mesh: TriangleMesh, threshold_angle_deg: float = 45.0, 
                         gravity_dir: Tuple[float,float,float] = (0,0,-1)) -> List[int]:
        """
        Identifies faces that require support structures.
        An overhang is a face whose normal points too far away from the gravity vector.
        """
        from .mesh_analysis import MeshAnalysis
        face_normals = MeshAnalysis.compute_face_normals(mesh)
        
        # Normalize gravity
        g_mag = math.sqrt(sum(x**2 for x in gravity_dir))
        g = (gravity_dir[0]/g_mag, gravity_dir[1]/g_mag, gravity_dir[2]/g_mag)
        
        # Overhang if angle between normal and gravity is small (normal points down)
        # Cos(theta) > cos(90 - threshold)
        limit_cos = math.cos(math.radians(90.0 - threshold_angle_deg))
        
        overhang_faces = []
        for i, n in enumerate(face_normals):
            # Dot product with -gravity (upward vector)
            dot = n[0]*(-g[0]) + n[1]*(-g[1]) + n[2]*(-g[2])
            if dot < limit_cos: # Points mostly "down"
                overhang_faces.append(i)
                
        return overhang_faces

    @staticmethod
    def estimate_print_time(mesh: TriangleMesh, layer_height: float, speed: float) -> float:
        """
        Provides a very rough estimate of 3D printing time based on surface area and layers.
        """
        from .mesh_analysis import MeshAnalysis
        bbox = mesh.bounding_box()
        height = bbox[1][2] - bbox[0][2]
        num_layers = height / layer_height
        
        area = MeshAnalysis.total_area(mesh)
        # Simplified: proportional to (Area * Layers) / Speed
        return (area * num_layers) / (speed * 100.0)
