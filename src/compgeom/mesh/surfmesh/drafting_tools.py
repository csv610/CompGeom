"""Mechanical Drafting and Tooling algorithms."""
import math
from typing import List, Tuple, Dict

from ..mesh import TriangleMesh
from ...kernel import Point3D

class DraftingTools:
    """Provides algorithms for mechanical part drafting and mold analysis."""

    @staticmethod
    def draft_analysis(mesh: TriangleMesh, pull_direction: Tuple[float, float, float], min_angle_deg: float) -> List[int]:
        """
        Identifies faces that violate the minimum draft angle.
        Essential for injection molding and casting design.
        """
        from .mesh_analysis import MeshAnalysis
        face_normals = MeshAnalysis.compute_face_normals(mesh)
        
        # Normalize pull direction
        mag = math.sqrt(sum(x**2 for x in pull_direction))
        pull = (pull_direction[0]/mag, pull_direction[1]/mag, pull_direction[2]/mag)
        
        violating_faces = []
        # Draft angle is 90 - angle between normal and pull direction
        # min_angle_deg requirement means cos(angle) < sin(min_angle)
        threshold_cos = math.cos(math.radians(90.0 - min_angle_deg))
        
        for i, normal in enumerate(face_normals):
            dot = normal[0]*pull[0] + normal[1]*pull[1] + normal[2]*pull[2]
            # Absolute dot because part can be pulled from either side of the mold midplane
            if abs(dot) < threshold_cos:
                violating_faces.append(i)
                
        return violating_faces

    @staticmethod
    def extract_silhouette(mesh: TriangleMesh, view_direction: Tuple[float, float, float]) -> List[Tuple[int, int]]:
        """
        Extracts the silhouette edges of the mesh from a given view direction.
        Fundamental for technical drafting and hidden line removal.
        """
        from .mesh_analysis import MeshAnalysis
        face_normals = MeshAnalysis.compute_face_normals(mesh)
        
        # Normalize view direction
        mag = math.sqrt(sum(x**2 for x in view_direction))
        view = (view_direction[0]/mag, view_direction[1]/mag, view_direction[2]/mag)
        
        edge_to_faces = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for j in range(3):
                edge = tuple(sorted((face[j], face[(j+1)%3])))
                edge_to_faces[edge].append(i)
                
        silhouette_edges = []
        for edge, incident_faces in edge_to_faces.items():
            if len(incident_faces) == 1:
                # Boundary edges are always part of the silhouette
                silhouette_edges.append(edge)
            elif len(incident_faces) == 2:
                # Silhouette edge is where one face faces the viewer and the other doesn't
                n1 = face_normals[incident_faces[0]]
                n2 = face_normals[incident_faces[1]]
                
                dot1 = n1[0]*view[0] + n1[1]*view[1] + n1[2]*view[2]
                dot2 = n2[0]*view[0] + n2[1]*view[1] + n2[2]*view[2]
                
                if (dot1 > 0 and dot2 <= 0) or (dot1 < 0 and dot2 >= 0):
                    silhouette_edges.append(edge)
                    
        return silhouette_edges
