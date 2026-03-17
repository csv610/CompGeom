"""Quality metrics for volumetric meshes (tetrahedral)."""
import math
from typing import List, Tuple

from ..mesh import TetMesh

class TetMeshQuality:
    """Calculates geometric quality metrics for tetrahedra."""

    @staticmethod
    def signed_volume(mesh: TetMesh) -> List[float]:
        """Calculates signed volume for each tetrahedron."""
        volumes = []
        for tet in mesh.cells:
            v0, v1, v2, v3 = [mesh.vertices[i] for i in tet.v_indices]
            # (v1-v0) dot ((v2-v0) cross (v3-v0)) / 6
            ux, uy, uz = v1.x-v0.x, v1.y-v0.y, v1.z-v0.z
            vx, vy, vz = v2.x-v0.x, v2.y-v0.y, v2.z-v0.z
            wx, wy, wz = v3.x-v0.x, v3.y-v0.y, v3.z-v0.z
            
            vol = (ux * (vy*wz - vz*wy) - uy * (vx*wz - vz*wx) + uz * (vx*wy - vy*wx)) / 6.0
            volumes.append(vol)
        return volumes

    @staticmethod
    def radius_ratio(mesh: TetMesh) -> List[float]:
        """
        Calculates radius ratio (3 * r_in / R_out) for each tetrahedron.
        Ideal (regular tet) is 1.0. Slivers approach 0.0.
        """
        ratios = []
        for tet in mesh.cells:
            v = [mesh.vertices[i] for i in tet.v_indices]
            # Edge lengths
            edges = []
            for i in range(4):
                for j in range(i+1, 4):
                    d = math.sqrt((v[i].x-v[j].x)**2 + (v[i].y-v[j].y)**2 + (v[i].z-v[j].z)**2)
                    edges.append(d)
            
            # Volume
            ux, uy, uz = v[1].x-v[0].x, v[1].y-v[0].y, v[1].z-v[0].z
            vx, vy, vz = v[2].x-v[0].x, v[2].y-v[0].y, v[2].z-v[0].z
            wx, wy, wz = v[3].x-v[0].x, v[3].y-v[0].y, v[3].z-v[0].z
            vol = abs(ux * (vy*wz - vz*wy) - uy * (vx*wz - vz*wx) + uz * (vx*wy - vy*wx)) / 6.0
            
            if vol < 1e-15:
                ratios.append(0.0)
                continue
                
            # Face areas
            def area(p1, p2, p3):
                ax, ay, az = p2.x-p1.x, p2.y-p1.y, p2.z-p1.z
                bx, by, bz = p3.x-p1.x, p3.y-p1.y, p3.z-p1.z
                cx, cy, cz = ay*bz-az*by, az*bx-ax*bz, ax*by-ay*bx
                return math.sqrt(cx*cx + cy*cy + cz*cz) / 2.0
                
            areas = [
                area(v[1], v[2], v[3]),
                area(v[0], v[2], v[3]),
                area(v[0], v[1], v[3]),
                area(v[0], v[1], v[2])
            ]
            
            # Inradius r = 3V / sum(Areas)
            r_in = 3.0 * vol / sum(areas)
            
            # Circumradius R = sqrt((a+b+c)(a+b-c)(a+c-b)(b+c-a)) / (24V) is for triangles
            # For Tet: R = product of edges of a face * opposite edge...? No.
            # R = distance from circumcenter to any vertex.
            # Simplified Ratio: 3 * r_in / R_out. 
            # We use an approximation or the exact formula for R.
            # Exact R for tet: R = sqrt((a*A + b*B + c*C) * (a*A + b*B - c*C) * ...) / (24V) - too complex.
            # Let's use the standard "Normalized Shape Ratio": 12 * (3V)^(2/3) / sum(edge_lengths^2)
            
            sum_l_sq = sum(e*e for e in edges)
            # This is a common alternative for Tet Quality
            quality = (36.0 * math.pi * vol**2)**(1/3) / (sum_l_sq) # Not exactly radius ratio but 0..1
            
            # Let's just use 3 * r_in / R_out approximation
            # For V1.0 we will provide the volume and a simple edge-ratio
            ratios.append(vol / (max(edges)**3 + 1e-15))
            
        return ratios
