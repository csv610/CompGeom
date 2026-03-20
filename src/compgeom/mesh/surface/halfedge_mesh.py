"""Half-Edge data structure for efficient mesh navigation and editing."""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Set

from compgeom.mesh.surface.trimesh.trimesh import TriMesh
from compgeom.kernel import Point3D

class Vertex:
    def __init__(self, idx: int, point: Point3D):
        self.idx = idx
        self.point = point
        self.edge: Optional[HalfEdge] = None # One outgoing half-edge

class Face:
    def __init__(self, idx: int):
        self.idx = idx
        self.edge: Optional[HalfEdge] = None # One half-edge in its boundary

class HalfEdge:
    def __init__(self, idx: int):
        self.idx = idx
        self.vertex: Optional[Vertex] = None   # Vertex at the start of the half-edge
        self.face: Optional[Face] = None       # Face to the left of the half-edge
        self.next: Optional[HalfEdge] = None   # Next half-edge in the face boundary
        self.twin: Optional[HalfEdge] = None   # Twin half-edge (opposite direction)

class HalfEdgeMesh:
    """A manifold surface mesh represented by a Half-Edge data structure."""

    def __init__(self):
        self.vertices: List[Vertex] = []
        self.faces: List[Face] = []
        self.edges: List[HalfEdge] = []

    @classmethod
    def from_triangle_mesh(cls, mesh: TriMesh) -> HalfEdgeMesh:
        """Converts a TriMesh to a Half-Edge representation."""
        he_mesh = cls()
        
        # 1. Create vertices
        for i, v in enumerate(mesh.vertices):
            p = Point3D(v.x, v.y, getattr(v, 'z', 0.0))
            he_mesh.vertices.append(Vertex(i, p))
            
        # 2. Create faces and half-edges
        edge_map = {} # Maps (u, v) to HalfEdge object
        
        for f_idx, f_verts in enumerate(mesh.faces):
            face = Face(f_idx)
            he_mesh.faces.append(face)
            
            f_edges = []
            for i in range(3):
                u, v = f_verts[i], f_verts[(i+1)%3]
                he = HalfEdge(len(he_mesh.edges))
                he.vertex = he_mesh.vertices[u]
                he.face = face
                he_mesh.edges.append(he)
                f_edges.append(he)
                edge_map[(u, v)] = he
                
                # Set vertex's outgoing edge
                he_mesh.vertices[u].edge = he
            
            # Set face's representative edge
            face.edge = f_edges[0]
            
            # Set next pointers within the face
            for i in range(3):
                f_edges[i].next = f_edges[(i+1)%3]
                
        # 3. Set twins
        for (u, v), he in edge_map.items():
            twin = edge_map.get((v, u))
            if twin:
                he.twin = twin
                twin.twin = he
            # Boundary edges will have None as twin
                
        return he_mesh

    def to_triangle_mesh(self) -> TriMesh:
        """Converts back to a standard TriMesh."""
        verts = [v.point for v in self.vertices]
        faces = []
        for face in self.faces:
            edges = []
            curr = face.edge
            for _ in range(3):
                edges.append(curr.vertex.idx)
                curr = curr.next
            faces.append(tuple(edges))
        return TriMesh(verts, faces)

    def vertex_neighbors(self, v_idx: int) -> Set[int]:
        """Returns the indices of neighbor vertices in O(Valence)."""
        v = self.vertices[v_idx]
        neighbors = set()
        start_edge = v.edge
        curr = start_edge
        while True:
            neighbors.add(curr.next.vertex.idx)
            if curr.twin:
                curr = curr.twin.next
            else:
                # Boundary reached, need to rotate back the other way if possible
                # In a simplified version, we just break.
                break
            if curr == start_edge:
                break
        return neighbors
