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
