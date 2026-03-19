from __future__ import annotations
from typing import List, Optional, Tuple, Union, Any

from compgeom.mesh.mesh_base import MeshNode, MeshFace, MeshEdge
from compgeom.mesh.surfmesh.trimesh.trimesh import TriMesh
from compgeom.mesh.surfmesh.surface_mesh import SurfaceMesh

class PolygonMesh(SurfaceMesh):
    """A 2D or 3D mesh composed of arbitrary polygonal faces."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Any]], 
                 faces: List[Union[MeshFace, Tuple[int, ...]]], 
                 edges: Optional[List[MeshEdge]] = None):
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Any, Any, Any]]) -> "PolygonMesh":
        """Converts a list of Point triangles to a PolygonMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        nodes = [MeshNode(i, p) for i, p in enumerate(unique_points)]
        faces = [MeshFace(i, (point_to_idx[t[0]], point_to_idx[t[1]], point_to_idx[t[2]])) for i, t in enumerate(triangles)]
            
        return cls(nodes, faces)

    @classmethod
    def from_file(cls, filename: str) -> PolygonMesh:
        """Creates a PolygonMesh from a file (OBJ, OFF, STL)."""
        from compgeom.mesh.surfmesh.meshio import MeshImporter
        mesh = MeshImporter.read(filename)
        return cls(mesh.nodes, mesh.faces)

    def triangulate(self) -> TriMesh:
        """
        Converts the polygon mesh into a triangle mesh using fan triangulation.
        Each polygon with n vertices is split into n-2 triangles.
        """
        tri_faces = []
        face_id = 0
        for face in self.faces:
            v = face.v_indices
            if len(v) == 3:
                tri_faces.append(MeshFace(face_id, v))
                face_id += 1
            elif len(v) > 3:
                for i in range(1, len(v) - 1):
                    tri_faces.append(MeshFace(face_id, (v[0], v[i], v[i+1])))
                    face_id += 1
        return TriMesh(self.nodes, tri_faces)
