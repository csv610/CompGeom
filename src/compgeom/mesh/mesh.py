"""Mesh data structures and topology helpers."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Set, Tuple, Union

from ..kernel import Point2D, Point3D


@dataclass(frozen=True)
class MeshNode:
    """A node in the mesh, representing a single point in space."""
    id: int
    point: Union[Point2D, Point3D]
    attributes: Dict = field(default_factory=dict)


@dataclass(frozen=True)
class MeshEdge:
    """An edge in the mesh, connecting two nodes."""
    id: int
    v_indices: Tuple[int, int]
    attributes: Dict = field(default_factory=dict)

    def __post_init__(self):
        # Ensure v_indices is a sorted tuple for undirected consistency
        if self.v_indices[0] > self.v_indices[1]:
            object.__setattr__(self, 'v_indices', (self.v_indices[1], self.v_indices[0]))


mesh_edges = MeshEdge


@dataclass(frozen=True)
class MeshFace:
    """A face in the mesh, defined by a sequence of vertex indices."""
    id: int
    v_indices: Tuple[int, ...]
    attributes: Dict = field(default_factory=dict)


@dataclass(frozen=True)
class MeshCell:
    """A volumetric cell in the mesh (e.g., tetrahedron, hexahedron)."""
    id: int
    v_indices: Tuple[int, ...]
    attributes: Dict = field(default_factory=dict)


class MeshTopology:
    """Provides topological queries for a mesh."""

    def __init__(self, mesh: Mesh):
        self._mesh = mesh
        self._v2v: Optional[Dict[int, Set[int]]] = None
        self._v2e: Optional[Dict[int, Set[int]]] = None
        self._e2e: Optional[Dict[int, Set[int]]] = None
        self._e2e_edge: Optional[Dict[int, Set[int]]] = None

    def vertex_neighbors(self, vertex_idx: int) -> Set[int]:
        """Returns the set of vertex indices adjacent to the given vertex."""
        if self._v2v is None:
            self._build_v2v()
        return self._v2v.get(vertex_idx, set())

    def vertex_elements(self, vertex_idx: int) -> Set[int]:
        """Returns the set of element indices (faces/cells) sharing the given vertex."""
        if self._v2e is None:
            self._build_v2e()
        return self._v2e.get(vertex_idx, set())

    def element_neighbors(self, element_idx: int) -> Set[int]:
        """Returns the set of element indices sharing at least one vertex."""
        if self._e2e is None:
            self._build_e2e()
        return self._e2e.get(element_idx, set())

    def shared_edge_neighbors(self, element_idx: int) -> Set[int]:
        """Returns the set of element indices sharing an edge (at least 2 vertices)."""
        if self._e2e_edge is None:
            self._build_e2e_edge()
        return self._e2e_edge.get(element_idx, set())

    def boundary_edges(self) -> List[Tuple[int, int]]:
        """Returns a list of edges (as vertex index pairs) that belong to only one element."""
        edge_count = defaultdict(int)
        
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for element in elements:
            n = len(element)
            for i in range(n):
                u, v = element[i], element[(i + 1) % n]
                edge = tuple(sorted((u, v)))
                edge_count[edge] += 1
        
        return [edge for edge, count in edge_count.items() if count == 1]

    def _build_v2v(self):
        self._v2v = defaultdict(set)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for element in elements:
            n = len(element)
            for i in range(n):
                u = element[i]
                v = element[(i + 1) % n]
                self._v2v[u].add(v)
                self._v2v[v].add(u)

    def _build_v2e(self):
        self._v2e = defaultdict(set)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for i, element in enumerate(elements):
            for v_idx in element:
                self._v2e[v_idx].add(i)

    def _build_e2e(self):
        """Builds adjacency based on shared vertices (at least one)."""
        if self._v2e is None:
            self._build_v2e()
        
        self._e2e = defaultdict(set)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for i, element in enumerate(elements):
            for v_idx in element:
                for neighbor_idx in self._v2e[v_idx]:
                    if neighbor_idx != i:
                        self._e2e[i].add(neighbor_idx)

    def _build_e2e_edge(self):
        """Builds adjacency based on shared edges (at least two vertices)."""
        self._e2e_edge = defaultdict(set)
        
        edge_map = defaultdict(list)
        elements = [c.v_indices for c in self._mesh.cells] if self._mesh.cells else [f.v_indices for f in self._mesh.faces]
        for i, element in enumerate(elements):
            n = len(element)
            for j in range(n):
                u, v = element[j], element[(j + 1) % n]
                edge = tuple(sorted((u, v)))
                edge_map[edge].append(i)
        
        for sharing_elements in edge_map.values():
            if len(sharing_elements) > 1:
                for i in range(len(sharing_elements)):
                    for j in range(i + 1, len(sharing_elements)):
                        u, v = sharing_elements[i], sharing_elements[j]
                        self._e2e_edge[u].add(v)
                        self._e2e_edge[v].add(u)


class Mesh(ABC):
    """Abstract base class for all mesh types."""

    def __init__(self, 
                 nodes: List[MeshNode], 
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None, 
                 cells: Optional[List[MeshCell]] = None):
        self._nodes = nodes
        self._edges = edges or []
        self._faces = faces or []
        self._cells = cells or []
        self._topology = MeshTopology(self)

    @property
    def nodes(self) -> List[MeshNode]:
        """Returns the list of nodes in the mesh."""
        return self._nodes

    @property
    def edges(self) -> List[MeshEdge]:
        """Returns the list of edges in the mesh."""
        return self._edges

    @property
    def faces(self) -> List[MeshFace]:
        """Returns the list of faces in the mesh."""
        return self._faces

    @property
    def cells(self) -> List[MeshCell]:
        """Returns the list of cells in the mesh."""
        return self._cells

    @property
    def vertices(self) -> List[Union[Point2D, Point3D]]:
        """Returns the list of points of the nodes."""
        return [node.point for node in self._nodes]

    @property
    def topology(self) -> MeshTopology:
        """Returns the topological helper for this mesh."""
        return self._topology

    def is_watertight(self) -> bool:
        """Returns True if the mesh is closed (no boundary edges)."""
        return len(self.topology.boundary_edges()) == 0

    @property
    def centroid(self) -> Union[Point2D, Point3D]:
        """Returns the geometric center of all nodes."""
        n = len(self._nodes)
        if n == 0:
            return Point2D(0, 0)
        
        sum_x = sum_y = sum_z = 0.0
        first_p = self._nodes[0].point
        is_3d = isinstance(first_p, Point3D)
        
        for node in self._nodes:
            p = node.point
            sum_x += p.x
            sum_y += p.y
            if is_3d:
                sum_z += getattr(p, 'z', 0.0)
        
        if is_3d:
            return Point3D(sum_x / n, sum_y / n, sum_z / n)
        return Point2D(sum_x / n, sum_y / n)

    def bounding_box(self) -> Tuple:
        """Returns the axis-aligned bounding box (min_coords, max_coords)."""
        if not self._nodes:
            return ()

        first_p = self._nodes[0].point
        is_3d = isinstance(first_p, Point3D)
        min_x = max_x = first_p.x
        min_y = max_y = first_p.y
        min_z = max_z = getattr(first_p, 'z', 0.0) if is_3d else 0.0

        for node in self._nodes[1:]:
            p = node.point
            if p.x < min_x: min_x = p.x
            elif p.x > max_x: max_x = p.x
            if p.y < min_y: min_y = p.y
            elif p.y > max_y: max_y = p.y
            if is_3d:
                vz = getattr(p, 'z', 0.0)
                if vz < min_z: min_z = vz
                elif vz > max_z: max_z = vz

        if is_3d:
            return (min_x, min_y, min_z), (max_x, max_y, max_z)
        
        return (min_x, min_y), (max_x, max_y)

    def translate(self, dx: float, dy: float, dz: float = 0.0):
        """Translates all nodes by (dx, dy, dz)."""
        new_nodes = []
        for node in self._nodes:
            p = node.point
            if isinstance(p, Point3D):
                new_p = Point3D(p.x + dx, p.y + dy, p.z + dz, getattr(p, 'id', -1))
            else:
                new_p = Point2D(p.x + dx, p.y + dy, getattr(p, 'id', -1))
            new_nodes.append(replace(node, point=new_p))
        self._nodes = new_nodes
        self._topology = MeshTopology(self)

    def scale(self, sx: float, sy: float, sz: float = 1.0):
        """Scales all nodes by (sx, sy, sz)."""
        new_nodes = []
        for node in self._nodes:
            p = node.point
            if isinstance(p, Point3D):
                new_p = Point3D(p.x * sx, p.y * sy, p.z * sz, getattr(p, 'id', -1))
            else:
                new_p = Point2D(p.x * sx, p.y * sy, getattr(p, 'id', -1))
            new_nodes.append(replace(node, point=new_p))
        self._nodes = new_nodes
        self._topology = MeshTopology(self)

    def rotate(self, angle_deg: float, axis: str = 'z'):
        """Rotates the mesh around an axis ('x', 'y', or 'z') by given degrees."""
        import math
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        new_nodes = []
        for node in self._nodes:
            p = node.point
            x, y = p.x, p.y
            z = getattr(p, 'z', 0.0)
            is_3d = isinstance(p, Point3D)
            
            if axis.lower() == 'x' and is_3d:
                ny = y * cos_a - z * sin_a
                nz = y * sin_a + z * cos_a
                new_p = Point3D(x, ny, nz, getattr(p, 'id', -1))
            elif axis.lower() == 'y' and is_3d:
                nx = x * cos_a + z * sin_a
                nz = -x * sin_a + z * cos_a
                new_p = Point3D(nx, y, nz, getattr(p, 'id', -1))
            else: # Default Z axis
                nx = x * cos_a - y * sin_a
                ny = x * sin_a + y * cos_a
                if is_3d:
                    new_p = Point3D(nx, ny, z, getattr(p, 'id', -1))
                else:
                    new_p = Point2D(nx, ny, getattr(p, 'id', -1))
            new_nodes.append(replace(node, point=new_p))
        self._nodes = new_nodes
        self._topology = MeshTopology(self)

    def normalize(self):
        """Centers the mesh at the origin and scales it to fit within a unit cube [-1, 1]."""
        bbox = self.bounding_box()
        if not bbox: return
        
        (min_x, min_y, *min_z), (max_x, max_y, *max_z) = bbox
        min_z = min_z[0] if min_z else 0.0
        max_z = max_z[0] if max_z else 0.0
        
        # Center
        cx, cy, cz = (min_x + max_x)/2, (min_y + max_y)/2, (min_z + max_z)/2
        self.translate(-cx, -cy, -cz)
        
        # Scale
        dx, dy, dz = max_x - min_x, max_y - min_y, max_z - min_z
        max_dim = max(dx, dy, dz, 1e-9)
        s = 2.0 / max_dim
        self.scale(s, s, s)

    def reorder_nodes(self, new_node_indices: List[int]):
        """
        Renumbers the nodes and updates element connectivity.
        """
        if len(new_node_indices) != len(self._nodes):
            raise ValueError("new_node_indices must have the same length as nodes.")

        old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(new_node_indices)}
        
        # New nodes with updated IDs
        new_nodes = []
        for new_idx, old_idx in enumerate(new_node_indices):
            node = self._nodes[old_idx]
            new_nodes.append(replace(node, id=new_idx))
        self._nodes = new_nodes

        # Update edges
        new_edges = []
        for edge in self._edges:
            new_v = tuple(old_to_new[v_idx] for v_idx in edge.v_indices)
            new_edges.append(replace(edge, v_indices=new_v))
        self._edges = new_edges

        # Update faces
        new_faces = []
        for face in self._faces:
            new_v = tuple(old_to_new[v_idx] for v_idx in face.v_indices)
            new_faces.append(replace(face, v_indices=new_v))
        self._faces = new_faces

        # Update cells
        new_cells = []
        for cell in self._cells:
            new_v = tuple(old_to_new[v_idx] for v_idx in cell.v_indices)
            new_cells.append(replace(cell, v_indices=new_v))
        self._cells = new_cells

        self._topology = MeshTopology(self)

    def to_file(self, filename: str, **kwargs):
        """Exports the mesh to a file.
        
        Args:
            filename: Path to the output file (detects format from extension).
            **kwargs: Format-specific options (e.g., binary=True).
        """
        from .meshio import MeshExporter
        MeshExporter.write(filename, self, **kwargs)


class TriangleMesh(Mesh):
    """A 2D or 3D mesh composed of triangular faces."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point2D, Point3D]], 
                 faces: List[Union[MeshFace, Tuple[int, ...]]], 
                 edges: Optional[List[MeshEdge]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if faces and not isinstance(faces[0], MeshFace):
            faces = [MeshFace(i, f) for i, f in enumerate(faces)]
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]]) -> TriangleMesh:
        """Converts a list of Point triangles to a TriangleMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        nodes = [MeshNode(i, p) for i, p in enumerate(unique_points)]
        
        faces = []
        for i, tri in enumerate(triangles):
            v_indices = (point_to_idx[tri[0]], point_to_idx[tri[1]], point_to_idx[tri[2]])
            faces.append(MeshFace(i, v_indices))
            
        return cls(nodes, faces)

    @classmethod
    def from_file(cls, filename: str) -> TriangleMesh:
        """Creates a TriangleMesh from a file (OBJ, OFF, STL)."""
        from .meshio import MeshImporter
        mesh = MeshImporter.read(filename)
        
        nodes = mesh.nodes
        tri_faces = []
        face_id = 0
        for face in mesh.faces:
            v = face.v_indices
            if len(v) == 3:
                tri_faces.append(MeshFace(face_id, v))
                face_id += 1
            elif len(v) > 3:
                for i in range(1, len(v) - 1):
                    tri_faces.append(MeshFace(face_id, (v[0], v[i], v[i+1])))
                    face_id += 1
        return cls(nodes, tri_faces)

    def euler_characteristic(self) -> int:
        v = len(self.nodes)
        f = len(self.faces)
        edges = set()
        for face in self.faces:
            v_indices = face.v_indices
            edges.add(tuple(sorted((v_indices[0], v_indices[1]))))
            edges.add(tuple(sorted((v_indices[1], v_indices[2]))))
            edges.add(tuple(sorted((v_indices[2], v_indices[0]))))
        e = len(edges)
        return v - e + f

    def ensure_even_elements(self) -> TriangleMesh:
        """
        Ensures the mesh has an even number of triangles.
        If count is odd:
        1. Try to find a boundary edge and split it (adds 1 triangle).
        2. If no boundary exists, split one triangle into 4 (adds 3 triangles).
        """
        if len(self.faces) % 2 == 0:
            return self

        mesh = self._split_one_to_four(self)
        if len(mesh.faces) % 2 != 0:
            mesh = self._split_one_edge(mesh)
        return mesh

    @staticmethod
    def _split_one_to_four(mesh: TriangleMesh) -> TriangleMesh:
        def get_area(f_idx):
            face = mesh.faces[f_idx]
            v0, v1, v2 = [mesh.nodes[i].point for i in face.v_indices]
            ax, ay, az = v0.x, v0.y, getattr(v0, 'z', 0.0)
            bx, by, bz = v1.x, v1.y, getattr(v1, 'z', 0.0)
            cx, cy, cz = v2.x, v2.y, getattr(v2, 'z', 0.0)
            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az
            cp_x, cp_y, cp_z = uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx
            return 0.5 * math.sqrt(cp_x**2 + cp_y**2 + cp_z**2)

        target_f_idx = max(range(len(mesh.faces)), key=get_area)
        target_face = mesh.faces[target_f_idx]
        target_v = target_face.v_indices
        
        edge_map = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            v = face.v_indices
            for j in range(3):
                edge = tuple(sorted((v[j], v[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        new_nodes = list(mesh.nodes)
        mid_indices = []
        edges = []
        for j in range(3):
            u_idx, v_idx = target_v[j], target_v[(j + 1) % 3]
            edge = tuple(sorted((u_idx, v_idx)))
            edges.append(edge)
            
            mid_idx = len(new_nodes)
            v1_p, v2_p = mesh.nodes[u_idx].point, mesh.nodes[v_idx].point
            if isinstance(v1_p, Point3D) and isinstance(v2_p, Point3D):
                mid_p = Point3D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2, (v1_p.z+v2_p.z)/2)
            else:
                mid_p = Point2D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2)
            new_nodes.append(MeshNode(mid_idx, mid_p))
            mid_indices.append(mid_idx)
            
        m01, m12, m20 = mid_indices
        v0, v1, v2 = target_v
        
        new_face_tuples = []
        new_face_tuples.extend([(v0, m01, m20), (v1, m12, m01), (v2, m20, m12), (m01, m12, m20)])
        
        split_neighbor_indices = set()
        for j in range(3):
            edge = edges[j]
            mid = mid_indices[j]
            neighbors = [i for i in edge_map[edge] if i != target_f_idx]
            for n_idx in neighbors:
                split_neighbor_indices.add(n_idx)
                n_face = mesh.faces[n_idx]
                n_v = n_face.v_indices
                opposite = [v for v in n_v if v not in edge][0]
                new_face_tuples.append((edge[0], mid, opposite))
                new_face_tuples.append((edge[1], mid, opposite))
                
        final_face_tuples = list(new_face_tuples)
        for i, face in enumerate(mesh.faces):
            if i == target_f_idx or i in split_neighbor_indices:
                continue
            final_face_tuples.append(face.v_indices)
            
        final_faces = [MeshFace(i, v) for i, v in enumerate(final_face_tuples)]
        return TriangleMesh(new_nodes, final_faces)

    @staticmethod
    def _split_one_edge(mesh: TriangleMesh) -> TriangleMesh:
        edge_map = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            v = face.v_indices
            for j in range(3):
                edge = tuple(sorted((v[j], v[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        boundary_edges = [e for e, faces in edge_map.items() if len(faces) == 1]
        
        if boundary_edges:
            edge = boundary_edges[0]
            f_idx = edge_map[edge][0]
            face = mesh.faces[f_idx]
            v_indices = face.v_indices
            new_nodes = list(mesh.nodes)
            mid_idx = len(new_nodes)
            v1_p, v2_p = mesh.nodes[edge[0]].point, mesh.nodes[edge[1]].point
            if isinstance(v1_p, Point3D) and isinstance(v2_p, Point3D):
                mid_p = Point3D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2, (v1_p.z+v2_p.z)/2)
            else:
                mid_p = Point2D((v1_p.x+v2_p.x)/2, (v1_p.y+v2_p.y)/2)
            new_nodes.append(MeshNode(mid_idx, mid_p))
            opposite = [v for v in v_indices if v not in edge][0]
            new_face_tuples = [(edge[0], mid_idx, opposite), (edge[1], mid_idx, opposite)]
            final_face_tuples = [f.v_indices for i, f in enumerate(mesh.faces) if i != f_idx] + new_face_tuples
            final_faces = [MeshFace(i, v) for i, v in enumerate(final_face_tuples)]
            return TriangleMesh(new_nodes, final_faces)
        return mesh


class QuadMesh(Mesh):
    """A 2D or 3D mesh composed of quadrilateral faces."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point2D, Point3D]], 
                 faces: List[Union[MeshFace, Tuple[int, ...]]], 
                 edges: Optional[List[MeshEdge]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if faces and not isinstance(faces[0], MeshFace):
            faces = [MeshFace(i, f) for i, f in enumerate(faces)]
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]]) -> "QuadMesh":
        """Converts a list of Point triangles to a QuadMesh object."""
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
    def from_file(cls, filename: str) -> QuadMesh:
        """Creates a QuadMesh from a file (OBJ, OFF, STL)."""
        from .meshio import MeshImporter
        mesh = MeshImporter.read(filename)
        return cls(mesh.nodes, mesh.faces)

    def extract_chord(self, start_quad_idx: int, edge_index: int) -> List[int]:
        """
        Extracts a topological chord starting from a given quad and its edge.
        A chord is a sequence of topologically parallel edges across adjacent quads.
        
        Extraction starts in both directions from the starting quad to ensure
        completeness, especially if one side ends at a boundary.
        
        Traversal stops if:
        1. A boundary edge is reached.
        2. The traversal returns to the starting quad and edge (closed loop).
        
        Args:
            start_quad_idx: Index of the starting quadrilateral.
            edge_index: Which edge of the quad to start from (0, 1, 2, or 3).
                        Parallel edge is (edge_index + 2) % 4.
                        
        Returns:
            A list of quadrilateral indices forming the chord.
        """
        if start_quad_idx < 0 or start_quad_idx >= len(self.faces):
            raise ValueError("Invalid quad index.")
            
        # Direction A: Forward extraction starting by crossing edge_index
        # We simulate entry from the opposite side
        path_forward, loop_f = self._traverse_chord_v2(start_quad_idx, (edge_index + 2) % 4, set())
        
        if loop_f:
            # If closed loop, the forward path already covers the cycle
            return [start_quad_idx] + path_forward

        # Direction B: Backward extraction starting by crossing opposite_edge_index
        # We simulate entry from edge_index
        path_backward, _ = self._traverse_chord_v2(start_quad_idx, edge_index, set(path_forward) | {start_quad_idx})
        
        # Assemble: reversed(backward) + start + forward
        return list(reversed(path_backward)) + [start_quad_idx] + path_forward

    def _traverse_chord_v2(self, start_idx: int, entry_edge_idx: int, global_visited: Set[int]) -> Tuple[List[int], bool]:
        path = []
        # State: (quad_idx, entry_edge_idx)
        visited_states = set()
        
        curr_idx = start_idx
        curr_entry = entry_edge_idx
        
        while True:
            # Exit from opposite side
            exit_edge_idx = (curr_entry + 2) % 4
            curr_face = self.faces[curr_idx]
            v_indices = curr_face.v_indices
            u, v = v_indices[exit_edge_idx], v_indices[(exit_edge_idx + 1) % 4]
            exit_edge = tuple(sorted((u, v)))
            
            # Find neighbor across exit_edge
            next_idx = None
            next_entry = -1
            
            for n_idx in self.topology.shared_edge_neighbors(curr_idx):
                n_face = self.faces[n_idx]
                n_v = n_face.v_indices
                n_edges = [tuple(sorted((n_v[k], n_v[(k + 1) % 4]))) for k in range(4)]
                if exit_edge in n_edges:
                    next_idx = n_idx
                    next_entry = n_edges.index(exit_edge)
                    break
            
            if next_idx is None:
                # Boundary reached (no neighbor sharing the exit edge)
                return path, False
            
            if next_idx == start_idx:
                # Returned to starting element
                return path, True
                
            if next_idx in global_visited or (next_idx, next_entry) in visited_states:
                # Collision with other part of the chord
                return path, False
                
            path.append(next_idx)
            visited_states.add((next_idx, next_entry))
            curr_idx = next_idx
            curr_entry = next_entry


class PolygonMesh(Mesh):
    """A 2D or 3D mesh composed of arbitrary polygonal faces."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point2D, Point3D]], 
                 faces: List[Union[MeshFace, Tuple[int, ...]]], 
                 edges: Optional[List[MeshEdge]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if faces and not isinstance(faces[0], MeshFace):
            faces = [MeshFace(i, f) for i, f in enumerate(faces)]
        super().__init__(nodes=nodes, faces=faces, edges=edges)

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]]) -> "PolygonMesh":
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
        from .meshio import MeshImporter
        mesh = MeshImporter.read(filename)
        return cls(mesh.nodes, mesh.faces)

    def triangulate(self) -> TriangleMesh:
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
        return TriangleMesh(self.nodes, tri_faces)

    def euler_characteristic(self) -> int:
        """Calculates the Euler characteristic (V - E + F)."""
        v = len(self.nodes)
        f = len(self.faces)
        edges = set()
        for face in self.faces:
            v_indices = face.v_indices
            n = len(v_indices)
            for i in range(n):
                u, v_node = v_indices[i], v_indices[(i + 1) % n]
                edges.add(tuple(sorted((u, v_node))))
        e = len(edges)
        return v - e + f


class TetMesh(Mesh):
    """A 3D volumetric mesh composed of tetrahedral cells."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point3D]], 
                 cells: List[Union[MeshCell, Tuple[int, int, int, int]]], 
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if cells and not isinstance(cells[0], MeshCell):
            cells = [MeshCell(i, c) for i, c in enumerate(cells)]
        super().__init__(nodes=nodes, cells=cells, edges=edges, faces=faces)


class HexMesh(Mesh):
    """A 3D volumetric mesh composed of hexahedral cells."""

    def __init__(self, 
                 nodes: List[Union[MeshNode, Point3D]], 
                 cells: List[Union[MeshCell, Tuple[int, int, int, int, int, int, int, int]]], 
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        if cells and not isinstance(cells[0], MeshCell):
            cells = [MeshCell(i, c) for i, c in enumerate(cells)]
        super().__init__(nodes=nodes, cells=cells, edges=edges, faces=faces)



__all__ = [
    "HexMesh",
    "Mesh",
    "MeshCell",
    "MeshEdge",
    "MeshFace",
    "MeshNode",
    "MeshTopology",
    "PolygonMesh",
    "QuadMesh",
    "TetMesh",
    "TriangleMesh",
]
