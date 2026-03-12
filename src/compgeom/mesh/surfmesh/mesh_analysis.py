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
    def detect_feature_edges(mesh: TriangleMesh, angle_threshold_degrees: float = 30.0) -> List[Tuple[int, int]]:
        """Detects sharp edges based on the dihedral angle between adjacent faces."""
        face_normals = MeshAnalysis.compute_face_normals(mesh)
        edge_to_faces = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for j in range(3):
                edge = tuple(sorted((face[j], face[(j+1)%3])))
                edge_to_faces[edge].append(i)
                
        threshold_cos = math.cos(math.radians(angle_threshold_degrees))
        feature_edges = []
        
        for edge, faces in edge_to_faces.items():
            if len(faces) == 1:
                # Boundary edges are always features
                feature_edges.append(edge)
            elif len(faces) == 2:
                n1 = face_normals[faces[0]]
                n2 = face_normals[faces[1]]
                dot = n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2]
                if dot < threshold_cos:
                    feature_edges.append(edge)
                    
        return feature_edges
