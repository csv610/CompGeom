"""Mesh quality metrics for surface meshes."""
import math
from typing import List, Dict, Tuple

from compgeom.mesh.surface.trimesh.trimesh import TriMesh

class MeshQuality:
    """Calculates geometric quality metrics for triangles."""

    @staticmethod
    def aspect_ratio(mesh: TriMesh) -> List[float]:
        """Calculates aspect ratio (R/r) for each triangle. Ideal is 1.0."""
        ratios = []
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            # Edges
            a = math.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2 + (p1[2]-p0[2])**2)
            b = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
            c = math.sqrt((p0[0]-p2[0])**2 + (p0[1]-p2[1])**2 + (p0[2]-p2[2])**2)
            
            s = (a + b + c) / 2.0
            area = math.sqrt(max(0, s * (s-a) * (s-b) * (s-c)))
            
            if area > 1e-12:
                # Aspect Ratio = (abc) / (8 * (s-a)(s-b)(s-c))
                # or simpler: R/2r where R=circumradius, r=inradius
                # r = area / s
                # R = abc / (4 * area)
                # AspectRatio = (abc * s) / (8 * area**2)
                ratio = (a * b * c * s) / (8.0 * area**2)
                ratios.append(ratio)
            else:
                ratios.append(float('inf'))
        return ratios

    @staticmethod
    def min_max_angles(mesh: TriMesh) -> List[Tuple[float, float]]:
        """Calculates minimum and maximum angles (in degrees) for each face."""
        angles = []
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            pts = [(v0.x, v0.y, getattr(v0, 'z', 0.0)),
                   (v1.x, v1.y, getattr(v1, 'z', 0.0)),
                   (v2.x, v2.y, getattr(v2, 'z', 0.0))]
            
            f_angles = []
            for i in range(3):
                p0 = pts[i]
                p1 = pts[(i+1)%3]
                p2 = pts[(i+2)%3]
                
                # Vectors from p0 to p1 and p0 to p2
                v_a = (p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2])
                v_b = (p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2])
                
                mag_a = math.sqrt(v_a[0]**2 + v_a[1]**2 + v_a[2]**2)
                mag_b = math.sqrt(v_b[0]**2 + v_b[1]**2 + v_b[2]**2)
                
                if mag_a > 1e-9 and mag_b > 1e-9:
                    dot = v_a[0]*v_b[0] + v_a[1]*v_b[1] + v_a[2]*v_b[2]
                    cos_theta = max(-1.0, min(1.0, dot / (mag_a * mag_b)))
                    f_angles.append(math.degrees(math.acos(cos_theta)))
                else:
                    f_angles.append(0.0)
            
            angles.append((min(f_angles), max(f_angles)))
        return angles
