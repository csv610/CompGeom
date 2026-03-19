from __future__ import annotations
from typing import List, Optional, Tuple, Union, Any

from compgeom.mesh.mesh_base import Mesh, MeshNode, MeshFace, MeshEdge

class SurfaceMesh(Mesh):
    """Base class for surface meshes (TriMesh, QuadMesh, PolygonMesh)."""
    
    def __init__(self, 
                 nodes: List[Union[MeshNode, Any]], 
                 faces: List[Union[MeshFace, Tuple[int, ...]]], 
                 edges: Optional[List[MeshEdge]] = None):
        """
        Initializes a surface mesh.
        
        Args:
            nodes: A list of nodes or points.
            faces: A list of faces or vertex indices.
            edges: An optional list of edges.
        """
        if faces and not isinstance(faces[0], MeshFace):
            faces = [MeshFace(i, f) for i, f in enumerate(faces)]
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    def euler_characteristic(self) -> int:
        """
        Computes the Euler characteristic of the surface mesh (V - E + F).
        
        Returns:
            The Euler characteristic as an integer.
        """
        v = len(self.nodes)
        f = len(self.faces)
        edges = set()
        for face in self.faces:
            v_indices = face.v_indices
            n = len(v_indices)
            for i in range(n):
                v1, v2 = v_indices[i], v_indices[(i + 1) % n]
                edges.add(tuple(sorted((v1, v2))))
        e = len(edges)
        return v - e + f
