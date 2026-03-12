"""Biomedical and Medical Device geometry algorithms."""
import math
from typing import List, Tuple, Dict, Optional

from ..mesh import TriangleMesh
from ...kernel import Point3D

class MedicalDeviceGeometry:
    """Provides algorithms for medical device design and bio-surface analysis."""

    @staticmethod
    def surface_roughness(mesh: TriangleMesh) -> float:
        """
        Calculates the Ra (Average Roughness) of the surface.
        In medical manufacturing (implants), surface finish is critical for osseointegration.
        """
        from .mesh_analysis import MeshAnalysis
        
        vertices = mesh.vertices
        v_normals = MeshAnalysis.compute_vertex_normals(mesh)
        
        # Calculate local deviations from the mean surface plane
        total_deviation = 0.0
        for i, v in enumerate(vertices):
            # Simple local deviation: distance to neighbors' centroid projected on normal
            neighbors = mesh.topology.vertex_neighbors(i)
            if not neighbors: continue
            
            sum_p = Point3D(0, 0, 0)
            for nb_idx in neighbors:
                nb = vertices[nb_idx]
                sum_p = Point3D(sum_p.x + nb.x, sum_p.y + nb.y, getattr(sum_p, 'z', 0.0) + getattr(nb, 'z', 0.0))
            
            centroid = Point3D(sum_p.x / len(neighbors), sum_p.y / len(neighbors), getattr(sum_p, 'z', 0.0) / len(neighbors))
            
            # Projection onto normal
            nx, ny, nz = v_normals[i]
            deviation = abs((v.x - centroid.x)*nx + (v.y - centroid.y)*ny + (getattr(v, 'z', 0.0) - getattr(centroid, 'z', 0.0))*nz)
            total_deviation += deviation
            
        return total_deviation / len(vertices)

    @staticmethod
    def stent_lattice_generator(radius: float, length: float, wire_thickness: float, cell_count_circular: int, cell_count_longitudinal: int) -> TriangleMesh:
        """
        Generates a 3D cylindrical lattice mesh representing a medical stent.
        Essential for interventional cardiology device design.
        """
        vertices = []
        faces = []
        
        for i in range(cell_count_longitudinal + 1):
            z = (i / cell_count_longitudinal) * length
            # Zig-zag pattern for stent cells
            offset = 0.5 if i % 2 == 1 else 0.0
            
            for j in range(cell_count_circular):
                angle = 2 * math.pi * (j + offset) / cell_count_circular
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                vertices.append(Point3D(x, y, z))
                
        # Connect vertices into a diamond/strut lattice (represented as triangles)
        for i in range(cell_count_longitudinal):
            for j in range(cell_count_circular):
                p1 = i * cell_count_circular + j
                p2 = (i + 1) * cell_count_circular + j
                p3 = (i + 1) * cell_count_circular + (j + 1) % cell_count_circular
                p4 = i * cell_count_circular + (j + 1) % cell_count_circular
                
                # Create thin triangles for struts
                faces.append((p1, p2, p3))
                faces.append((p1, p3, p4))
                
        return TriangleMesh(vertices, faces)

    @staticmethod
    def porosity_analysis(mesh: TriangleMesh, volume_bbox: float) -> float:
        """
        Calculates the porosity percentage of a 3D printed lattice/bone scaffold.
        Ratio of empty space to total volume.
        """
        from .mesh_analysis import MeshAnalysis
        material_vol = abs(MeshAnalysis.total_volume(mesh))
        return (1.0 - (material_vol / volume_bbox)) * 100.0
