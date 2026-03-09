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

    def ensure_even_elements(self) -> TriangleMesh:
        """
        Ensures the mesh has an even number of triangles.
        If count is odd:
        1. Try to find a boundary edge and split it (adds 1 triangle).
        2. If no boundary exists, split one triangle into 4 (adds 3 triangles).
        """
        if len(self.faces) % 2 == 0:
            return self

        # 1. Look for boundary edges
        edge_map = defaultdict(list)
        for i, face in enumerate(self.faces):
            for j in range(3):
                edge = tuple(sorted((face[j], face[(j + 1) % 3])))
                edge_map[edge].append(i)
        
        boundary_edges = [e for e, faces in edge_map.items() if len(faces) == 1]
        
        if boundary_edges:
            # Simple boundary split: N -> N+1 (even)
            edge = boundary_edges[0]
            f_idx = edge_map[edge][0]
            face = self.faces[f_idx]
            
            new_vertices = list(self.vertices)
            mid_idx = len(new_vertices)
            v1, v2 = self.vertices[edge[0]], self.vertices[edge[1]]
            if isinstance(v1, Point3D) and isinstance(v2, Point3D):
                mid = Point3D((v1.x+v2.x)/2, (v1.y+v2.y)/2, (v1.z+v2.z)/2, mid_idx)
            else:
                mid = Point((v1.x+v2.x)/2, (v1.y+v2.y)/2, mid_idx)
            new_vertices.append(mid)
            
            opposite = [v for v in face if v not in edge][0]
            new_faces = [(edge[0], mid, opposite), (edge[1], mid, opposite)]
            
            final_faces = [f for i, f in enumerate(self.faces) if i != f_idx] + new_faces
            return TriangleMesh(new_vertices, final_faces)
        else:
            # Closed mesh: N -> N+3 (even) by splitting one triangle into 4
            new_vertices = list(self.vertices)
            target_face = self.faces[0]
            
            # Midpoints for the 3 edges
            m_indices = []
            for j in range(3):
                u, v = target_face[j], target_face[(j + 1) % 3]
                idx = len(new_vertices)
                p1, p2 = self.vertices[u], self.vertices[v]
                if isinstance(p1, Point3D):
                    m = Point3D((p1.x+p2.x)/2, (p1.y+p2.y)/2, (p1.z+p2.z)/2, idx)
                else:
                    m = Point((p1.x+p2.x)/2, (p1.y+p2.y)/2, idx)
                new_vertices.append(m)
                m_indices.append(idx)
            
            v0, v1, v2 = target_face
            m0, m1, m2 = m_indices
            
            new_sub_faces = [(v0, m0, m2), (v1, m1, m0), (v2, m2, m1), (m0, m1, m2)]
            final_faces = list(self.faces[1:]) + new_sub_faces
            return TriangleMesh(new_vertices, final_faces)


class QuadMesh(Mesh):
...
