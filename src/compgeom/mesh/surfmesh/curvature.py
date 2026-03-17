"""Curvature estimation for surface meshes."""
import math
from collections import defaultdict
from typing import List, Tuple

from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
from ...kernel import Point3D

class MeshCurvature:
    """Calculates Gaussian and Mean curvature at mesh vertices."""

    @staticmethod
    def gaussian_curvature(mesh: TriMesh) -> List[float]:
        """
        Calculates Gaussian curvature using the angle deficit method.
        K_i = (2*pi - sum(theta_ij)) / A_i
        """
        vertices = mesh.vertices
        faces = mesh.faces
        num_vertices = len(vertices)
        
        angle_sums = [0.0] * num_vertices
        areas = [0.0] * num_vertices
        
        for face in faces:
            v0, v1, v2 = [vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            # Edges
            e0 = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
            e1 = (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
            e2 = (p0[0]-p2[0], p0[1]-p2[1], p0[2]-p2[2])
            
            # Lengths squared
            l0 = e0[0]**2 + e0[1]**2 + e0[2]**2
            l1 = e1[0]**2 + e1[1]**2 + e1[2]**2
            l2 = e2[0]**2 + e2[1]**2 + e2[2]**2
            
            # Triangle area (cross product magnitude / 2)
            cross_x = e0[1]*(-e2[2]) - e0[2]*(-e2[1])
            cross_y = e0[2]*(-e2[0]) - e0[0]*(-e2[2])
            cross_z = e0[0]*(-e2[1]) - e0[1]*(-e2[0])
            area = math.sqrt(cross_x**2 + cross_y**2 + cross_z**2) / 2.0
            
            # Angles via dot product
            def get_angle(a, b):
                mag_a = math.sqrt(a[0]**2 + a[1]**2 + a[2]**2)
                mag_b = math.sqrt(b[0]**2 + b[1]**2 + b[2]**2)
                if mag_a < 1e-9 or mag_b < 1e-9: return 0.0
                dot = a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
                val = max(-1.0, min(1.0, dot / (mag_a * mag_b)))
                return math.acos(val)
                
            angle0 = get_angle((p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]), (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]))
            angle1 = get_angle((p0[0]-p1[0], p0[1]-p1[1], p0[2]-p1[2]), (p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]))
            angle2 = get_angle((p0[0]-p2[0], p0[1]-p2[1], p0[2]-p2[2]), (p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]))
            
            angle_sums[face[0]] += angle0
            angle_sums[face[1]] += angle1
            angle_sums[face[2]] += angle2
            
            areas[face[0]] += area / 3.0
            areas[face[1]] += area / 3.0
            areas[face[2]] += area / 3.0
            
        curvatures = []
        for i in range(num_vertices):
            if areas[i] < 1e-9:
                curvatures.append(0.0)
            else:
                k = (2 * math.pi - angle_sums[i]) / areas[i]
                curvatures.append(k)
                
        return curvatures

    @staticmethod
    def mean_curvature(mesh: TriMesh) -> List[float]:
        """
        Calculates Mean curvature magnitude using the cotangent Laplacian.
        |H_i| = 0.5 * |Laplace-Beltrami(v_i)|
        """
        vertices = mesh.vertices
        faces = mesh.faces
        num_vertices = len(vertices)
        
        laplacian = [[0.0, 0.0, 0.0] for _ in range(num_vertices)]
        areas = [0.0] * num_vertices
        
        # We need cotangents of angles opposite to edges
        for face in faces:
            v0, v1, v2 = [vertices[i] for i in face]
            pts = [
                (v0.x, v0.y, getattr(v0, 'z', 0.0)),
                (v1.x, v1.y, getattr(v1, 'z', 0.0)),
                (v2.x, v2.y, getattr(v2, 'z', 0.0))
            ]
            
            for i in range(3):
                # Edge is from pts[i] to pts[(i+1)%3]
                # Opposite vertex is pts[(i+2)%3]
                p0 = pts[i]
                p1 = pts[(i+1)%3]
                p2 = pts[(i+2)%3]
                
                v_a = (p0[0]-p2[0], p0[1]-p2[1], p0[2]-p2[2])
                v_b = (p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2])
                
                cross_x = v_a[1]*v_b[2] - v_a[2]*v_b[1]
                cross_y = v_a[2]*v_b[0] - v_a[0]*v_b[2]
                cross_z = v_a[0]*v_b[1] - v_a[1]*v_b[0]
                area = math.sqrt(cross_x**2 + cross_y**2 + cross_z**2) / 2.0
                
                dot = v_a[0]*v_b[0] + v_a[1]*v_b[1] + v_a[2]*v_b[2]
                
                if area > 1e-9:
                    cot_alpha = dot / (2.0 * area)
                else:
                    cot_alpha = 0.0
                    
                idx0 = face[i]
                idx1 = face[(i+1)%3]
                
                laplacian[idx0][0] += cot_alpha * (pts[1][0] - pts[0][0])
                laplacian[idx0][1] += cot_alpha * (pts[1][1] - pts[0][1])
                laplacian[idx0][2] += cot_alpha * (pts[1][2] - pts[0][2])
                
                laplacian[idx1][0] += cot_alpha * (pts[0][0] - pts[1][0])
                laplacian[idx1][1] += cot_alpha * (pts[0][1] - pts[1][1])
                laplacian[idx1][2] += cot_alpha * (pts[0][2] - pts[1][2])
                
                areas[idx0] += area / 3.0
                areas[idx1] += area / 3.0
                areas[face[(i+2)%3]] += area / 3.0
                
        curvatures = []
        for i in range(num_vertices):
            if areas[i] < 1e-9:
                curvatures.append(0.0)
            else:
                lx = laplacian[i][0] / (2.0 * areas[i])
                ly = laplacian[i][1] / (2.0 * areas[i])
                lz = laplacian[i][2] / (2.0 * areas[i])
                mag = math.sqrt(lx**2 + ly**2 + lz**2)
                curvatures.append(0.5 * mag)
                
        return curvatures
