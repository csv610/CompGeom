"""Topographical analysis for Civil Engineering (TIN and Contouring)."""
from typing import List, Tuple
import math

from compgeom.mesh import TriangleMesh
from compgeom.kernel import Point3D
from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
from compgeom.mesh.surfmesh.mesh_queries import MeshQueries

class TopoAnalysis:
    """Provides algorithms for terrain modeling and contour extraction."""

    @staticmethod
    def extract_contours(mesh: TriangleMesh, elevation: float) -> List[List[Point3D]]:
        """
        Extracts elevation isocontours from a terrain mesh.
        Returns a list of polylines (contours) at the specified height.
        """
        # This is a specialized slice_mesh for horizontal planes
        segments = MeshQueries.slice_mesh(mesh, (0, 0, elevation), (0, 0, 1))
        
        # Connect segments into polylines
        if not segments: return []
        
        polylines = []
        visited = [False] * len(segments)
        
        for i in range(len(segments)):
            if visited[i]: continue
            
            current_poly = [segments[i][0], segments[i][1]]
            visited[i] = True
            
            # Greedy search for next segment
            found = True
            while found:
                found = False
                for j in range(len(segments)):
                    if visited[j]: continue
                    
                    p1, p2 = segments[j]
                    tail = current_poly[-1]
                    
                    def dist(a, b): return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2 + (a.z-b.z)**2)
                    
                    if dist(tail, p1) < 1e-8:
                        current_poly.append(p2)
                        visited[j] = True
                        found = True
                        break
                    elif dist(tail, p2) < 1e-8:
                        current_poly.append(p1)
                        visited[j] = True
                        found = True
                        break
            polylines.append(current_poly)
            
        return polylines

    @staticmethod
    def earthwork_volume(mesh_base: TriangleMesh, mesh_top: TriangleMesh) -> float:
        """
        Calculates the volume of soil/material between two surfaces.
        Essential for civil engineering construction sites.
        """
        vol_base = MeshAnalysis.total_volume(mesh_base) # Assumes closed to Z=0
        vol_top = MeshAnalysis.total_volume(mesh_top)
        return vol_top - vol_base
