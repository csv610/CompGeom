"""Mesh data structures and topology helpers."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Union

from ..geometry import Point, Point3D


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
                for j in range(i + 1, n):
                    v = element[j]
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

    def __init__(self, vertices: List[Union[Point, Point3D]], elements: List[Tuple[int, ...]]):
        self._vertices = vertices
        self._elements = elements
        self._topology = MeshTopology(self)

    @property
    def vertices(self) -> List[Union[Point, Point3D]]:
        """Returns the list of vertices in the mesh."""
        return self._vertices

    @property
    def elements(self) -> List[Tuple[int, ...]]:
        """Returns the list of element indices (faces or cells)."""
        return self._elements

    @property
    def topology(self) -> MeshTopology:
        """Returns the topological helper for this mesh."""
        return self._topology

    @property
    def centroid(self) -> Union[Point, Point3D]:
        """Returns the geometric center of all vertices."""
        if not self._vertices:
            return Point(0, 0)
        
        avg_x = sum(v.x for v in self._vertices) / len(self._vertices)
        avg_y = sum(v.y for v in self._vertices) / len(self._vertices)
        
        if isinstance(self._vertices[0], Point3D):
            avg_z = sum(v.z for v in self._vertices) / len(self._vertices)
            return Point3D(avg_x, avg_y, avg_z)
        return Point(avg_x, avg_y)

    def bounding_box(self) -> Tuple:
        """Returns the axis-aligned bounding box (min_coords, max_coords)."""
        if not self._vertices:
            return ()

        min_x = min(v.x for v in self._vertices)
        max_x = max(v.x for v in self._vertices)
        min_y = min(v.y for v in self._vertices)
        max_y = max(v.y for v in self._vertices)

        if isinstance(self._vertices[0], Point3D):
            min_z = min(v.z for v in self._vertices)
            max_z = max(v.z for v in self._vertices)
            return (min_x, min_y, min_z), (max_x, max_y, max_z)
        
        return (min_x, min_y), (max_x, max_y)

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
    def from_file(cls, filename: str) -> TriangleMesh:
        """Creates a TriangleMesh from an OBJ file."""
        from .mesh_io import OBJFileHandler
        vertices, faces = OBJFileHandler.read(filename)
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
                mid = Point((v1.x+v2.x)/2, (v1.y+v2.y)/2, mid_idx)
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
            mid = Point3D((v1.x+v2.x)/2, (v1.y+v2.y)/2, (v1.z+v2.z)/2, mid_idx) if isinstance(v1, Point3D) else Point((v1.x+v2.x)/2, (v1.y+v2.y)/2, mid_idx)
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
    def from_file(cls, filename: str) -> QuadMesh:
        """Creates a QuadMesh from an OBJ file."""
        from .mesh_io import OBJFileHandler
        vertices, faces = OBJFileHandler.read(filename)
        # Assumes faces are quads
        return cls(vertices, faces)


class TetMesh(Mesh):
    """A 3D volumetric mesh composed of tetrahedral cells."""

    def __init__(self, vertices: List[Point3D], tets: List[Tuple[int, int, int, int]]):
        super().__init__(vertices, tets)

    @property
    def cells(self) -> List[Tuple[int, int, int, int]]:
        return self._elements


class HexMesh(Mesh):
    """A 3D volumetric mesh composed of hexahedral cells."""

    def __init__(self, vertices: List[Point3D], hexas: List[Tuple[int, int, int, int, int, int, int, int]]):
        super().__init__(vertices, hexas)

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
    "QuadMesh",
    "TetMesh",
    "TriangleMesh",
    "euler_characteristic",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "vertex_neighbors",
]
