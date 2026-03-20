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
        if not v.edge: return neighbors
        
        # In a triangle mesh, rotate around the vertex
        # Starting edge is v -> nb
        curr = v.edge
        
        # Rotate CCW
        while True:
            neighbors.add(curr.next.vertex.idx)
            if not curr.twin: break
            curr = curr.twin.next
            if curr == v.edge: return neighbors # Closed fan
            
        # If we broke because of boundary, rotate CW from original start
        curr = v.edge
        while True:
            # To rotate CW: go to the edge that ends at v in the previous triangle
            # Tri is (v, nb, prev_v). Edge is nb -> v (twin of v -> nb). 
            # Prev tri edge ending at v is prev_v -> v.
            # In our tri (v, nb, next_v), next_v -> v is curr.next.next
            
            # Actually, just get the start vertex of the edge that ends at v
            # If curr is v -> nb, then curr.next.next is nb_prev -> v.
            # Its twin is v -> nb_prev.
            cw_edge = curr.next.next.twin
            if not cw_edge:
                # One more neighbor on the boundary
                neighbors.add(curr.next.next.vertex.idx)
                break
            curr = cw_edge
            neighbors.add(curr.next.vertex.idx)
            if curr == v.edge: break
            
        return neighbors

    def get_half_edge(self, u_idx: int, v_idx: int) -> Optional[HalfEdge]:
        """Returns the half-edge from vertex u to vertex v, if it exists."""
        v = self.vertices[u_idx]
        curr = v.edge
        if not curr: return None
        start = curr
        while True:
            if curr.next.vertex.idx == v_idx:
                return curr
            if not curr.twin: break
            curr = curr.twin.next
            if curr == start: break
        return None
