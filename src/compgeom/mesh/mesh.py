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
        
        # Map edge (sorted tuple of 2 vertices) to elements sharing it
        edge_map = defaultdict(list)
        for i, element in enumerate(self._mesh.elements):
            n = len(element)
            for j in range(n):
                # For polygons (triangle, quad), edges are adjacent vertices
                # For polyhedra (tet, hex), we also check adjacent pairs in face definitions
                # Simplified: check all pairs in the element for any dimension
                for k in range(j + 1, n):
                    edge = tuple(sorted((element[j], element[k])))
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


class TriangleMesh(Mesh):
    """A 2D or 3D mesh composed of triangular faces."""

    @property
    def faces(self) -> List[Tuple[int, int, int]]:
        return self._elements

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


class QuadMesh(Mesh):
    """A 2D or 3D mesh composed of quadrilateral faces."""

    @property
    def faces(self) -> List[Tuple[int, int, int, int]]:
        return self._elements


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
