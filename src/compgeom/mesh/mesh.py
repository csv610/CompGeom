"""Mesh data structures and topology helpers."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Union

from ..kernel import Point2D, Point3D


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
        
        for element in self._mesh.elements:
            n = len(element)
            for i in range(n):
                u, v = element[i], element[(i + 1) % n]
                edge = tuple(sorted((u, v)))
                edge_count[edge] += 1
        
        return [edge for edge, count in edge_count.items() if count == 1]

    def _build_v2v(self):
        self._v2v = defaultdict(set)
        for element in self._mesh.elements:
            n = len(element)
            for i in range(n):
                u = element[i]
                v = element[(i + 1) % n]
                self._v2v[u].add(v)
                self._v2v[v].add(u)

    def _build_v2e(self):
        self._v2e = defaultdict(set)
        for i, element in enumerate(self._mesh.elements):
            for v_idx in element:
                self._v2e[v_idx].add(i)

    def _build_e2e(self):
        """Builds adjacency based on shared vertices (at least one)."""
        if self._v2e is None:
            self._build_v2e()
        
        self._e2e = defaultdict(set)
        for i, element in enumerate(self._mesh.elements):
            for v_idx in element:
                for neighbor_idx in self._v2e[v_idx]:
                    if neighbor_idx != i:
                        self._e2e[i].add(neighbor_idx)

    def _build_e2e_edge(self):
        """Builds adjacency based on shared edges (at least two vertices)."""
        self._e2e_edge = defaultdict(set)
        
        edge_map = defaultdict(list)
        for i, element in enumerate(self._mesh.elements):
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

    def __init__(self, vertices: List[Union[Point2D, Point3D]], elements: List[Tuple[int, ...]], skipped_points: Optional[List[Tuple[Point2D, str]]] = None):
        self._vertices = vertices
        self._elements = elements
        self._skipped_points = skipped_points or []
        self._topology = MeshTopology(self)

    @property
    def vertices(self) -> List[Union[Point2D, Point3D]]:
        """Returns the list of vertices in the mesh."""
        return self._vertices

    @property
    def elements(self) -> List[Tuple[int, ...]]:
        """Returns the list of element indices (faces or cells)."""
        return self._elements

    @property
    def skipped_points(self) -> List[Tuple[Point2D, str]]:
        """Returns points that were skipped during mesh generation (e.g., duplicates)."""
        return self._skipped_points

    @property
    def topology(self) -> MeshTopology:
        """Returns the topological helper for this mesh."""
        return self._topology

    def is_watertight(self) -> bool:
        """Returns True if the mesh is closed (no boundary edges)."""
        return len(self.topology.boundary_edges()) == 0

    @property
    def centroid(self) -> Union[Point2D, Point3D]:
        """Returns the geometric center of all vertices."""
        n = len(self._vertices)
        if n == 0:
            return Point2D(0, 0)
        
        sum_x = sum_y = sum_z = 0.0
        is_3d = isinstance(self._vertices[0], Point3D)
        
        for v in self._vertices:
            sum_x += v.x
            sum_y += v.y
            if is_3d:
                sum_z += v.z
        
        if is_3d:
            return Point3D(sum_x / n, sum_y / n, sum_z / n)
        return Point2D(sum_x / n, sum_y / n)

    def bounding_box(self) -> Tuple:
        """Returns the axis-aligned bounding box (min_coords, max_coords)."""
        if not self._vertices:
            return ()

        is_3d = isinstance(self._vertices[0], Point3D)
        first = self._vertices[0]
        min_x = max_x = first.x
        min_y = max_y = first.y
        min_z = max_z = getattr(first, 'z', 0.0) if is_3d else 0.0

        for v in self._vertices[1:]:
            if v.x < min_x: min_x = v.x
            elif v.x > max_x: max_x = v.x
            if v.y < min_y: min_y = v.y
            elif v.y > max_y: max_y = v.y
            if is_3d:
                vz = v.z
                if vz < min_z: min_z = vz
                elif vz > max_z: max_z = vz

        if is_3d:
            return (min_x, min_y, min_z), (max_x, max_y, max_z)
        
        return (min_x, min_y), (max_x, max_y)

    def translate(self, dx: float, dy: float, dz: float = 0.0):
        """Translates all vertices by (dx, dy, dz)."""
        is_3d = isinstance(self._vertices[0], Point3D)
        for i, v in enumerate(self._vertices):
            if is_3d:
                self._vertices[i] = Point3D(v.x + dx, v.y + dy, v.z + dz, getattr(v, 'id', -1))
            else:
                self._vertices[i] = Point2D(v.x + dx, v.y + dy, getattr(v, 'id', -1))
        self._topology = MeshTopology(self)

    def scale(self, sx: float, sy: float, sz: float = 1.0):
        """Scales all vertices by (sx, sy, sz)."""
        is_3d = isinstance(self._vertices[0], Point3D)
        for i, v in enumerate(self._vertices):
            if is_3d:
                self._vertices[i] = Point3D(v.x * sx, v.y * sy, v.z * sz, getattr(v, 'id', -1))
            else:
                self._vertices[i] = Point2D(v.x * sx, v.y * sy, getattr(v, 'id', -1))
        self._topology = MeshTopology(self)

    def rotate(self, angle_deg: float, axis: str = 'z'):
        """Rotates the mesh around an axis ('x', 'y', or 'z') by given degrees."""
        import math
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        is_3d = isinstance(self._vertices[0], Point3D)
        
        for i, v in enumerate(self._vertices):
            x, y = v.x, v.y
            z = getattr(v, 'z', 0.0)
            
            if axis.lower() == 'x' and is_3d:
                ny = y * cos_a - z * sin_a
                nz = y * sin_a + z * cos_a
                self._vertices[i] = Point3D(x, ny, nz, getattr(v, 'id', -1))
            elif axis.lower() == 'y' and is_3d:
                nx = x * cos_a + z * sin_a
                nz = -x * sin_a + z * cos_a
                self._vertices[i] = Point3D(nx, y, nz, getattr(v, 'id', -1))
            else: # Default Z axis
                nx = x * cos_a - y * sin_a
                ny = x * sin_a + y * cos_a
                if is_3d:
                    self._vertices[i] = Point3D(nx, ny, z, getattr(v, 'id', -1))
                else:
                    self._vertices[i] = Point2D(nx, ny, getattr(v, 'id', -1))
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
        Renumbers the vertices and updates element connectivity.
        
        Args:
            new_node_indices: A list where the value at index i is the old vertex index
                             that should now be at position i.
        """
        if len(new_node_indices) != len(self._vertices):
            raise ValueError("new_node_indices must have the same length as vertices.")

        old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(new_node_indices)}
        self._vertices = [self._vertices[i] for i in new_node_indices]
        new_elements = []
        for element in self._elements:
            new_elements.append(tuple(old_to_new[v_idx] for v_idx in element))
        self._elements = new_elements
        self._topology = MeshTopology(self)


class TriangleMesh(Mesh):
    """A 2D or 3D mesh composed of triangular faces."""

    @property
    def faces(self) -> List[Tuple[int, int, int]]:
        return self._elements

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]], skipped_points: Optional[List[Tuple[Point2D, str]]] = None) -> TriangleMesh:
        """Converts a list of Point triangles to a TriangleMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        faces = []
        for tri in triangles:
            faces.append((point_to_idx[tri[0]], point_to_idx[tri[1]], point_to_idx[tri[2]]))
            
        return cls(unique_points, faces, skipped_points=skipped_points)

    @classmethod
    def from_file(cls, filename: str) -> TriangleMesh:
        """Creates a TriangleMesh from a file (OBJ, OFF, STL)."""
        from .meshio import MeshImporter, OBJFileHandler
        vertices, faces = MeshImporter.read(filename)
        # Ensure triangles
        tri_faces = OBJFileHandler.triangulate_faces(faces)
        return cls(vertices, tri_faces)

    def euler_characteristic(self) -> int:
        v = len(self._vertices)
        f = len(self._elements)
        edges = set()
        for face in self._elements:
            edges.add(tuple(sorted((face[0], face[1]))))
            edges.add(tuple(sorted((face[1], face[2]))))
            edges.add(tuple(sorted((face[2], face[0]))))
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
            v0, v1, v2 = [mesh.vertices[i] for i in mesh.faces[f_idx]]
            ax, ay, az = v0.x, v0.y, getattr(v0, 'z', 0.0)
            bx, by, bz = v1.x, v1.y, getattr(v1, 'z', 0.0)
            cx, cy, cz = v2.x, v2.y, getattr(v2, 'z', 0.0)
            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az
            cp_x, cp_y, cp_z = uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx
            return 0.5 * math.sqrt(cp_x**2 + cp_y**2 + cp_z**2)

        target_f_idx = max(range(len(mesh.faces)), key=get_area)
        target_face = mesh.faces[target_f_idx]
        
        edge_map = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for j in range(3):
                edge = tuple(sorted((face[j], face[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        new_vertices = list(mesh.vertices)
        mid_indices = []
        edges = []
        for j in range(3):
            u_idx, v_idx = target_face[j], target_face[(j + 1) % 3]
            edge = tuple(sorted((u_idx, v_idx)))
            edges.append(edge)
            
            mid_idx = len(new_vertices)
            v1, v2 = mesh.vertices[u_idx], mesh.vertices[v_idx]
            if isinstance(v1, Point3D) and isinstance(v2, Point3D):
                mid = Point3D((v1.x+v2.x)/2, (v1.y+v2.y)/2, (v1.z+v2.z)/2, mid_idx)
            else:
                mid = Point2D((v1.x+v2.x)/2, (v1.y+v2.y)/2, mid_idx)
            new_vertices.append(mid)
            mid_indices.append(mid_idx)
            
        m01, m12, m20 = mid_indices
        v0, v1, v2 = target_face
        
        new_faces = []
        new_faces.extend([(v0, m01, m20), (v1, m12, m01), (v2, m20, m12), (m01, m12, m20)])
        
        split_neighbor_indices = set()
        for j in range(3):
            edge = edges[j]
            mid = mid_indices[j]
            neighbors = [i for i in edge_map[edge] if i != target_f_idx]
            for n_idx in neighbors:
                split_neighbor_indices.add(n_idx)
                n_face = mesh.faces[n_idx]
                opposite = [v for v in n_face if v not in edge][0]
                new_faces.append((edge[0], mid, opposite))
                new_faces.append((edge[1], mid, opposite))
                
        final_faces = list(new_faces)
        for i, face in enumerate(mesh.faces):
            if i == target_f_idx or i in split_neighbor_indices:
                continue
            final_faces.append(face)
            
        return TriangleMesh(new_vertices, final_faces)

    @staticmethod
    def _split_one_edge(mesh: TriangleMesh) -> TriangleMesh:
        edge_map = defaultdict(list)
        for i, face in enumerate(mesh.faces):
            for j in range(3):
                edge = tuple(sorted((face[j], face[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        boundary_edges = [e for e, faces in edge_map.items() if len(faces) == 1]
        
        if boundary_edges:
            edge = boundary_edges[0]
            f_idx = edge_map[edge][0]
            face = mesh.faces[f_idx]
            new_vertices = list(mesh.vertices)
            mid_idx = len(new_vertices)
            v1, v2 = mesh.vertices[edge[0]], mesh.vertices[edge[1]]
            mid = Point3D((v1.x+v2.x)/2, (v1.y+v2.y)/2, (v1.z+v2.z)/2, mid_idx) if isinstance(v1, Point3D) else Point2D((v1.x+v2.x)/2, (v1.y+v2.y)/2, mid_idx)
            new_vertices.append(mid)
            opposite = [v for v in face if v not in edge][0]
            new_faces = [(edge[0], mid, opposite), (edge[1], mid, opposite)]
            final_faces = [f for i, f in enumerate(mesh.faces) if i != f_idx] + new_faces
            return TriangleMesh(new_vertices, final_faces)
        return mesh


class QuadMesh(Mesh):
    """A 2D or 3D mesh composed of quadrilateral faces."""

    @property
    def faces(self) -> List[Tuple[int, int, int, int]]:
        return self._elements

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]], skipped_points: Optional[List[Tuple[Point2D, str]]] = None) -> TriangleMesh:
        """Converts a list of Point triangles to a TriangleMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        faces = []
        for tri in triangles:
            faces.append((point_to_idx[tri[0]], point_to_idx[tri[1]], point_to_idx[tri[2]]))
            
        return cls(unique_points, faces, skipped_points=skipped_points)

    @classmethod
    def from_file(cls, filename: str) -> QuadMesh:
        """Creates a QuadMesh from a file (OBJ, OFF, STL)."""
        from .meshio import MeshImporter
        vertices, faces = MeshImporter.read(filename)
        # Assumes faces are quads
        return cls(vertices, faces)

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
            u, v = curr_face[exit_edge_idx], curr_face[(exit_edge_idx + 1) % 4]
            exit_edge = tuple(sorted((u, v)))
            
            # Find neighbor across exit_edge
            next_idx = None
            next_entry = -1
            
            for n_idx in self.topology.shared_edge_neighbors(curr_idx):
                n_face = self.faces[n_idx]
                n_edges = [tuple(sorted((n_face[k], n_face[(k + 1) % 4]))) for k in range(4)]
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

    @property
    def faces(self) -> List[Tuple[int, ...]]:
        return self._elements

    @classmethod
    def from_triangles(cls, triangles: List[Tuple[Point2D, Point2D, Point2D]], skipped_points: Optional[List[Tuple[Point2D, str]]] = None) -> TriangleMesh:
        """Converts a list of Point triangles to a TriangleMesh object."""
        unique_points = []
        point_to_idx = {}
        
        for tri in triangles:
            for p in tri:
                if p not in point_to_idx:
                    point_to_idx[p] = len(unique_points)
                    unique_points.append(p)
        
        faces = []
        for tri in triangles:
            faces.append((point_to_idx[tri[0]], point_to_idx[tri[1]], point_to_idx[tri[2]]))
            
        return cls(unique_points, faces, skipped_points=skipped_points)

    @classmethod
    def from_file(cls, filename: str) -> PolygonMesh:
        """Creates a PolygonMesh from a file (OBJ, OFF, STL)."""
        from .meshio import MeshImporter
        vertices, faces = MeshImporter.read(filename)
        return cls(vertices, [tuple(f) for f in faces])

    def triangulate(self) -> TriangleMesh:
        """
        Converts the polygon mesh into a triangle mesh using fan triangulation.
        Each polygon with n vertices is split into n-2 triangles.
        """
        from .meshio import OBJFileHandler
        tri_faces = OBJFileHandler.triangulate_faces(self._elements)
        return TriangleMesh(self._vertices, tri_faces)

    def euler_characteristic(self) -> int:
        """Calculates the Euler characteristic (V - E + F)."""
        v = len(self._vertices)
        f = len(self._elements)
        edges = set()
        for face in self._elements:
            n = len(face)
            for i in range(n):
                u, v_idx = face[i], face[(i + 1) % n]
                edges.add(tuple(sorted((u, v_idx))))
        e = len(edges)
        return v - e + f


class TetMesh(Mesh):
    """A 3D volumetric mesh composed of tetrahedral cells."""

    def __init__(self, vertices: List[Point3D], tets: List[Tuple[int, int, int, int]], skipped_points: Optional[List[Tuple[Point2D, str]]] = None):
        super().__init__(vertices, tets, skipped_points)

    @property
    def cells(self) -> List[Tuple[int, int, int, int]]:
        return self._elements


class HexMesh(Mesh):
    """A 3D volumetric mesh composed of hexahedral cells."""

    def __init__(self, vertices: List[Point3D], hexas: List[Tuple[int, int, int, int, int, int, int, int]], skipped_points: Optional[List[Tuple[Point2D, str]]] = None):
        super().__init__(vertices, hexas, skipped_points)

    @property
    def cells(self) -> List[Tuple[int, int, int, int, int, int, int, int]]:
        return self._elements


def mesh_edges(triangles):
    edges = set()
    for a, b, c in triangles:
        edges.add(tuple(sorted((a.id, b.id))))
        edges.add(tuple(sorted((b.id, c.id))))
        edges.add(tuple(sorted((c.id, a.id))))
    return edges


def mesh_vertices(triangles):
    vertices = {}
    for triangle in triangles:
        for vertex in triangle:
            vertices[vertex.id] = vertex
    return vertices


def euler_characteristic(triangles):
    vertices = mesh_vertices(triangles)
    edges = mesh_edges(triangles)
    faces = len(triangles)
    chi = len(vertices) - len(edges) + faces
    return {
        "vertices": len(vertices),
        "edges": len(edges),
        "faces": faces,
        "euler_characteristic": chi,
    }


def vertex_neighbors(triangles):
    neighbors = defaultdict(set)
    for a, b, c in triangles:
        neighbors[a.id].update([b.id, c.id])
        neighbors[b.id].update([a.id, c.id])
        neighbors[c.id].update([a.id, b.id])
    return {vertex_id: sorted(adjacent) for vertex_id, adjacent in neighbors.items()}


def triangle_neighbors(triangles):
    edge_to_triangles = defaultdict(list)
    for triangle_index, (a, b, c) in enumerate(triangles):
        edge_to_triangles[tuple(sorted((a.id, b.id)))].append(triangle_index)
        edge_to_triangles[tuple(sorted((b.id, c.id)))].append(triangle_index)
        edge_to_triangles[tuple(sorted((c.id, a.id)))].append(triangle_index)

    neighbors = {triangle_index: set() for triangle_index in range(len(triangles))}
    for owners in edge_to_triangles.values():
        if len(owners) != 2:
            continue
        left, right = owners
        neighbors[left].add(right)
        neighbors[right].add(left)
    return {triangle_index: sorted(adjacent) for triangle_index, adjacent in neighbors.items()}


def mesh_neighbors(triangles):
    return {
        "vertex_neighbors": vertex_neighbors(triangles),
        "triangle_neighbors": triangle_neighbors(triangles),
    }


__all__ = [
    "HexMesh",
    "Mesh",
    "MeshTopology",
    "PolygonMesh",
    "QuadMesh",
    "TetMesh",
    "TriangleMesh",
    "from_triangles",
    "euler_characteristic",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "vertex_neighbors",
]
