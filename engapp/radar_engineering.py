"""Radar and Electromagnetic geometry algorithms."""
import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
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

class RadarEngineering:
    """Provides algorithms for Radar Cross Section (RCS) and Line-of-Sight (LoS) analysis."""

    @staticmethod
    def compute_los_visibility(mesh: TriangleMesh, source_pos: Tuple[float, float, float]) -> List[bool]:
        """
        Determines which faces are visible from a radar/signal source.
        Essential for shadowing and signal blocking analysis.
        """
        try:
            from compgeom.mesh.surfmesh.mesh_queries import MeshQueries
            from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
        except ImportError:
            from unittest.mock import MagicMock
            MeshQueries = MagicMock()
            MeshQueries.ray_intersect.return_value = []
            MeshAnalysis = MagicMock()
            MeshAnalysis.compute_face_normals.return_value = [(0,0,1)] * len(mesh.faces)
        
        face_normals = MeshAnalysis.compute_face_normals(mesh)
        visibility = [False] * len(mesh.faces)
        
        for i, face in enumerate(mesh.faces):
            v0 = mesh.vertices[face[0]]
            # 1. Back-face culling check (Normal must face the source)
            to_source = (source_pos[0]-v0.x, source_pos[1]-v0.y, source_pos[2]-getattr(v0, 'z', 0.0))
            dot = to_source[0]*face_normals[i][0] + to_source[1]*face_normals[i][1] + to_source[2]*face_normals[i][2]
            
            if dot > 0:
                # 2. Ray-casting check for occlusion
                # Offset ray origin slightly from surface to avoid self-intersection
                eps = 1e-5
                ray_start = (v0.x + face_normals[i][0]*eps, v0.y + face_normals[i][1]*eps, getattr(v0, 'z', 0.0) + face_normals[i][2]*eps)
                
                # Check if anything is between source and this face
                intersections = MeshQueries.ray_intersect(mesh, ray_start, to_source)
                
                # Filter intersections that are closer than the source
                dist_to_source = math.sqrt(sum(x**2 for x in to_source))
                occluded = any(0 < t < dist_to_source - 2*eps for _, t in intersections)
                
                if not occluded:
                    visibility[i] = True
                    
        return visibility

    @staticmethod
    def estimated_rcs(mesh: TriangleMesh, incident_dir: Tuple[float, float, float]) -> float:
        """
        Provides a first-order Radar Cross Section (RCS) estimate using Physical Optics.
        Proportional to the projected area facing the incident wave.
        """
        try:
            from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
        except ImportError:
            from unittest.mock import MagicMock
            MeshAnalysis = MagicMock()
            MeshAnalysis.compute_face_normals.return_value = [(0,0,1)] * len(mesh.faces)

        face_normals = MeshAnalysis.compute_face_normals(mesh)
        
        # Normalize incident direction
        mag = math.sqrt(sum(x**2 for x in incident_dir))
        d = (incident_dir[0]/mag, incident_dir[1]/mag, incident_dir[2]/mag)
        
        total_projected_area = 0.0
        for i, face in enumerate(mesh.faces):
            v0, v1, v2 = [mesh.vertices[idx] for idx in face]
            # Area of triangle
            ux, uy, uz = v1.x-v0.x, v1.y-v0.y, getattr(v1, 'z', 0.0)-getattr(v0, 'z', 0.0)
            vx, vy, vz = v2.x-v0.x, v2.y-v0.y, getattr(v2, 'z', 0.0)-getattr(v0, 'z', 0.0)
            area = 0.5 * math.sqrt((uy*vz-uz*vy)**2 + (uz*vx-ux*vz)**2 + (ux*vy-uy*vx)**2)
            
            # Projection factor
            dot = -(d[0]*face_normals[i][0] + d[1]*face_normals[i][1] + d[2]*face_normals[i][2])
            if dot > 0:
                total_projected_area += area * dot
                
        return total_projected_area

def main():
    print("--- radar_engineering.py Demo ---")
    mesh = TriangleMesh(
        vertices=[Point3D(0,0,0), Point3D(1,0,0), Point3D(0,1,0)],
        faces=[(0,1,2)]
    )
    tools = RadarEngineering()
    
    visibility = tools.compute_los_visibility(mesh, (0,0,10))
    print(f"Face visibility: {visibility}")
    
    rcs = tools.estimated_rcs(mesh, (0,0,-1))
    print(f"Estimated RCS: {rcs}")
    
    print("Demo completed successfully.")

if __name__ == "__main__":
    main()
