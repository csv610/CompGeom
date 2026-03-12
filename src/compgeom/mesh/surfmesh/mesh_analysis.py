"""Mesh analysis algorithms: normals, curvature, and features."""
from collections import defaultdict
import math
from typing import List, Tuple, Dict

from ..mesh import TriangleMesh

class MeshAnalysis:
    """Provides algorithms for analyzing surface meshes."""

    @staticmethod
    def compute_face_normals(mesh: TriangleMesh) -> List[Tuple[float, float, float]]:
        """Computes the normal vector for each face in the mesh."""
        normals = []
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            ux, uy, uz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
            vx, vy, vz = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
            
            nx = uy*vz - uz*vy
            ny = uz*vx - ux*vz
            nz = ux*vy - uy*vx
            
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 1e-9:
                normals.append((nx/length, ny/length, nz/length))
            else:
                normals.append((0.0, 0.0, 0.0))
        return normals

    @staticmethod
    def compute_vertex_normals(mesh: TriangleMesh) -> List[Tuple[float, float, float]]:
        """Computes area-weighted vertex normals for smooth shading."""
        v_normals = [[0.0, 0.0, 0.0] for _ in range(len(mesh.vertices))]
        
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            ux, uy, uz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
            vx, vy, vz = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
            
            # Cross product magnitude represents 2x face area
            nx = uy*vz - uz*vy
            ny = uz*vx - ux*vz
            nz = ux*vy - uy*vx
            
            for idx in face:
                v_normals[idx][0] += nx
                v_normals[idx][1] += ny
                v_normals[idx][2] += nz
                
        # Normalize
        res = []
        for nx, ny, nz in v_normals:
            length = math.sqrt(nx*nx + ny*ny + nz*nz)
            if length > 1e-9:
                res.append((nx/length, ny/length, nz/length))
            else:
                res.append((0.0, 0.0, 0.0))
        return res

    @staticmethod
    def total_area(mesh: TriangleMesh) -> float:
        """Calculates the total surface area of the mesh."""
        total = 0.0
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            ux, uy, uz = v1.x-v0.x, v1.y-v0.y, getattr(v1, 'z', 0.0)-getattr(v0, 'z', 0.0)
            vx, vy, vz = v2.x-v0.x, v2.y-v0.y, getattr(v2, 'z', 0.0)-getattr(v0, 'z', 0.0)
            cx = uy*vz - uz*vy
            cy = uz*vx - ux*vz
            cz = ux*vy - uy*vx
            total += 0.5 * math.sqrt(cx*cx + cy*cy + cz*cz)
        return total

    @staticmethod
    def total_volume(mesh: TriangleMesh) -> float:
        """Calculates the total volume enclosed by the surface using the divergence theorem."""
        total = 0.0
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            # p0 dot (p1 cross p2) / 6
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            total += (p0[0] * (p1[1]*p2[2] - p1[2]*p2[1]) + 
                      p0[1] * (p1[2]*p2[0] - p1[0]*p2[2]) + 
                      p0[2] * (p1[0]*p2[1] - p1[1]*p2[0])) / 6.0
        return total

    @staticmethod
    def center_of_mass(mesh: TriangleMesh) -> Tuple[float, float, float]:
        """Calculates the center of mass (centroid) of the volume enclosed by the surface."""
        total_vol = 0.0
        cx, cy, cz = 0.0, 0.0, 0.0
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            # Volume of tet formed with origin
            vol = (p0[0] * (p1[1]*p2[2] - p1[2]*p2[1]) + 
                   p0[1] * (p1[2]*p2[0] - p1[0]*p2[2]) + 
                   p0[2] * (p1[0]*p2[1] - p1[1]*p2[0])) / 6.0
            
            # Centroid of this tet
            tx = (p0[0] + p1[0] + p2[0]) / 4.0
            ty = (p0[1] + p1[1] + p2[1]) / 4.0
            tz = (p0[2] + p1[2] + p2[2]) / 4.0
            
            cx += tx * vol
            cy += ty * vol
            cz += tz * vol
            total_vol += vol
            
        if abs(total_vol) < 1e-12:
            return mesh.centroid.x, mesh.centroid.y, getattr(mesh.centroid, 'z', 0.0)
            
        return cx/total_vol, cy/total_vol, cz/total_vol

    @staticmethod
    def inertia_tensor(mesh: TriangleMesh) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]:
        """
        Calculates the 3x3 inertia tensor matrix (assuming uniform unit density).
        Returns a tuple of 3 tuples: ((Ixx, Ixy, Ixz), (Iyx, Iyy, Iyz), (Izx, Izy, Izz)).
        """
        # Based on David Eberly's Polyhedral Mass Properties
        mult = [1/6, 1/24, 1/24, 1/24, 1/60, 1/60, 1/60, 1/120, 1/120, 1/120]
        intg = [0.0] * 10
        
        for face in mesh.faces:
            v0, v1, v2 = [mesh.vertices[i] for i in face]
            p0 = (v0.x, v0.y, getattr(v0, 'z', 0.0))
            p1 = (v1.x, v1.y, getattr(v1, 'z', 0.0))
            p2 = (v2.x, v2.y, getattr(v2, 'z', 0.0))
            
            a1, b1, c1 = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
            a2, b2, c2 = p2[0]-p0[0], p2[1]-p0[1], p2[2]-p0[2]
            d0, d1, d2 = b1*c2 - b2*c1, a2*c1 - a1*c2, a1*b2 - a2*b1
            
            f1x = p0[0] + p1[0] + p2[0]
            f1y = p0[1] + p1[1] + p2[1]
            f1z = p0[2] + p1[2] + p2[2]
            
            f2x = p0[0]**2 + p1[0]**2 + p2[0]**2 + f1x**2
            f2y = p0[1]**2 + p1[1]**2 + p2[1]**2 + f1y**2
            f2z = p0[2]**2 + p1[2]**2 + p2[2]**2 + f1z**2
            
            f3x = p0[0]**3 + p1[0]**3 + p2[0]**3 + f1x * f2x
            f3y = p0[1]**3 + p1[1]**3 + p2[1]**3 + f1y * f2y
            f3z = p0[2]**3 + p1[2]**3 + p2[2]**3 + f1z * f2z
            
            g0x = f2x + p0[0] * (f1x + p0[0])
            g0y = f2y + p0[1] * (f1y + p0[1])
            g0z = f2z + p0[2] * (f1z + p0[2])
            
            g1x = f2x + p1[0] * (f1x + p1[0])
            g1y = f2y + p1[1] * (f1y + p1[1])
            g1z = f2z + p1[2] * (f1z + p1[2])
            
            g2x = f2x + p2[0] * (f1x + p2[0])
            g2y = f2y + p2[1] * (f1y + p2[1])
            g2z = f2z + p2[2] * (f1z + p2[2])
            
            fxyz = p0[0] * b1 * g0z + p1[0] * b2 * g1z + p2[0] * (b1 + b2) * g2z # simplified integral components
            
            intg[0] += d0 * f1x
            intg[1] += d0 * f2x
            intg[2] += d1 * f2y
            intg[3] += d2 * f2z
            intg[4] += d0 * f3x
            intg[5] += d1 * f3y
            intg[6] += d2 * f3z
            
            # Cross terms
            temp0 = p0[0] + p1[0]
            temp1 = p0[1] + p1[1]
            temp2 = p0[2] + p1[2]
            
            # Approximated fast cross terms for physics engines
            f_x_y = p0[0]*p0[1] + p1[0]*p1[1] + p2[0]*p2[1] + (p0[0]+p1[0]+p2[0])*(p0[1]+p1[1]+p2[1])
            f_y_z = p0[1]*p0[2] + p1[1]*p1[2] + p2[1]*p2[2] + (p0[1]+p1[1]+p2[1])*(p0[2]+p1[2]+p2[2])
            f_z_x = p0[2]*p0[0] + p1[2]*p1[0] + p2[2]*p2[0] + (p0[2]+p1[2]+p2[2])*(p0[0]+p1[0]+p2[0])
            
            intg[7] += d0 * f_x_y
            intg[8] += d1 * f_y_z
            intg[9] += d2 * f_z_x

        for i in range(10): intg[i] *= mult[i]
        
        mass = intg[0]
        # Translate to center of mass
        cm_x, cm_y, cm_z = intg[1]/mass, intg[2]/mass, intg[3]/mass
        
        # Inertia tensor relative to origin
        ixx = intg[5] + intg[6]
        iyy = intg[4] + intg[6]
        izz = intg[4] + intg[5]
        ixy = -intg[7]
        iyz = -intg[8]
        izx = -intg[9]
        
        # Parallel axis theorem to move to COM
        ixx -= mass * (cm_y**2 + cm_z**2)
        iyy -= mass * (cm_z**2 + cm_x**2)
        izz -= mass * (cm_x**2 + cm_y**2)
        ixy += mass * cm_x * cm_y
        iyz += mass * cm_y * cm_z
        izx += mass * cm_z * cm_x
        
        return (
            (ixx, ixy, izx),
            (ixy, iyy, iyz),
            (izx, iyz, izz)
        )
