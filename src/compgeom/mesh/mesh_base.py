"""Base classes for mesh data structures and topology."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Set, Tuple, Union

from compgeom.kernel import Point2D, Point3D


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
            object.__setattr__(self, "v_indices", (self.v_indices[1], self.v_indices[0]))


@dataclass(frozen=True)
class MeshFace:
    """A face in the mesh, defined by a sequence of vertex indices."""

    id: int
    v_indices: Tuple[int, ...]
    attributes: Dict = field(default_factory=dict)

    def __iter__(self):
        return iter(self.v_indices)

    def __len__(self):
        return len(self.v_indices)

    def __getitem__(self, index):
        return self.v_indices[index]

    def __eq__(self, other):
        if isinstance(other, tuple):
            return self.v_indices == other
        if isinstance(other, MeshFace):
            return self.id == other.id and self.v_indices == other.v_indices and self.attributes == other.attributes
        return False


@dataclass(frozen=True)
class MeshCell:
    """A volumetric cell in the mesh (e.g., tetrahedron, hexahedron)."""

    id: int
    v_indices: Tuple[int, ...]
    attributes: Dict = field(default_factory=dict)

    def __iter__(self):
        return iter(self.v_indices)

    def __len__(self):
        return len(self.v_indices)

    def __getitem__(self, index):
        return self.v_indices[index]


class Mesh(ABC):
    """Abstract base class for all mesh types."""

    def __init__(
        self,
        nodes: Optional[List[Union[MeshNode, Point2D, Point3D]]] = None,
        edges: Optional[List[MeshEdge]] = None,
        faces: Optional[List[MeshFace]] = None,
        cells: Optional[List[MeshCell]] = None,
    ):
        if nodes:
            if not isinstance(nodes[0], MeshNode):
                nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        else:
            nodes = []

        if edges:
            if not isinstance(edges[0], MeshEdge):
                edges = [MeshEdge(i, tuple(e)) for i, e in enumerate(edges)]
        else:
            edges = []

        if faces:
            if not isinstance(faces[0], MeshFace):
                faces = [MeshFace(i, tuple(f)) for i, f in enumerate(faces)]
        else:
            faces = []

        if cells:
            if not isinstance(cells[0], MeshCell):
                cells = [MeshCell(i, tuple(c)) for i, c in enumerate(cells)]
        else:
            cells = []

        self._nodes = nodes
        self._edges = edges
        self._faces = faces
        self._cells = cells

    @property
    def nodes(self) -> List[MeshNode]:
        """Returns the list of nodes in the mesh."""
        return self._nodes

    @nodes.setter
    def nodes(self, value: List[Union[MeshNode, Point2D, Point3D]]):
        """Sets nodes and re-indexes them."""
        if value:
            if not isinstance(value[0], MeshNode):
                value = [MeshNode(i, p) for i, p in enumerate(value)]
        self._nodes = value

    @property
    def edges(self) -> List[MeshEdge]:
        """Returns the list of edges in the mesh."""
        return self._edges

    @edges.setter
    def edges(self, value: List[Union[MeshEdge, Tuple[int, ...]]]):
        """Sets edges."""
        if value:
            if not isinstance(value[0], MeshEdge):
                value = [MeshEdge(i, tuple(e)) for i, e in enumerate(value)]
        self._edges = value

    @property
    def faces(self) -> List[MeshFace]:
        """Returns the list of faces in the mesh."""
        return self._faces

    @faces.setter
    def faces(self, value: List[Union[MeshFace, Tuple[int, ...]]]):
        """Sets faces and auto-extracts edges if this is a surface mesh."""
        if value:
            if not isinstance(value[0], MeshFace):
                value = [MeshFace(i, tuple(f)) for i, f in enumerate(value)]
        self._faces = value
        if self._cells:
            from compgeom.mesh.mesh_topology import MeshTopology

            self._faces = MeshTopology.extract_faces(self._cells)
            self._edges = MeshTopology.extract_edges(self._faces)
        elif self._faces:
            from compgeom.mesh.mesh_topology import MeshTopology

            self._edges = MeshTopology.extract_edges(self._faces)

    @property
    def cells(self) -> List[MeshCell]:
        """Returns the list of cells in the mesh."""
        return self._cells

    @property
    def topology(self):
        """Returns a MeshTopology object for this mesh."""
        from compgeom.mesh.mesh_topology import MeshTopology
        return MeshTopology(self)

    @cells.setter
    def cells(self, value: List[Union[MeshCell, Tuple[int, ...]]]):
        """Sets cells and auto-extracts faces and edges."""
        if value:
            if not isinstance(value[0], MeshCell):
                value = [MeshCell(i, tuple(c)) for i, c in enumerate(value)]

        added_cells = []
        removed_cell_ids = set()

        if self._cells and value:
            old_ids = {c.id for c in self._cells}
            new_ids = {c.id for c in value}
            removed_cell_ids = old_ids - new_ids
            added_ids = new_ids - old_ids
            added_cells = [c for c in value if c.id in added_ids]

        self._cells = value

        if self._cells:
            self._recompute_topology_from_cells(removed_cell_ids, added_cells)

    def add_faces(self, faces: List[Union[MeshFace, Tuple[int, ...]]]):
        """Adds faces and updates edges."""
        from compgeom.mesh.mesh_topology import MeshTopology

        new_faces = []
        for f in faces:
            if isinstance(f, MeshFace):
                new_faces.append(f)
            else:
                new_faces.append(MeshFace(len(self._faces) + len(new_faces), tuple(f)))

        self._faces.extend(new_faces)

        if self._cells:
            self._faces = MeshTopology.extract_faces(self._cells)
            self._edges = MeshTopology.extract_edges(self._faces)
        else:
            new_edges = MeshTopology.extract_edges(self._faces)
            existing_keys = {e.v_indices for e in self._edges}
            for edge in new_edges:
                if edge.v_indices not in existing_keys:
                    self._edges.append(MeshEdge(len(self._edges), edge.v_indices))

    def remove_faces(self, face_ids: Set[int]):
        """Removes faces by ID and cleans up unused edges."""
        if not face_ids:
            return

        self._faces = [f for f in self._faces if f.id not in face_ids]

        if self._cells:
            from compgeom.mesh.mesh_topology import MeshTopology

            self._faces = MeshTopology.extract_faces(self._cells)
            self._edges = MeshTopology.extract_edges(self._faces)
        else:
            used_edges = set()
            for face in self._faces:
                v = face.v_indices
                for i in range(len(v)):
                    a, b = v[i], v[(i + 1) % len(v)]
                    used_edges.add((min(a, b), max(a, b)))
            self._edges = [e for e in self._edges if e.v_indices in used_edges]

    def add_cells(self, cells: List[Union[MeshCell, Tuple[int, ...]]]):
        """Adds cells and updates faces and edges."""
        new_cells = []
        for c in cells:
            if isinstance(c, MeshCell):
                new_cells.append(c)
            else:
                new_cells.append(MeshCell(len(self._cells) + len(new_cells), tuple(c)))

        self._cells.extend(new_cells)

        from compgeom.mesh.mesh_topology import MeshTopology

        self._faces = MeshTopology.extract_faces(self._cells)
        self._edges = MeshTopology.extract_edges(self._faces)

    def remove_cells(self, cell_ids: Set[int]):
        """Removes cells by ID and cleans up unused faces and edges."""
        if not cell_ids:
            return

        self._cells = [c for c in self._cells if c.id not in cell_ids]

        from compgeom.mesh.mesh_topology import MeshTopology

        self._faces = MeshTopology.extract_faces(self._cells)
        self._edges = MeshTopology.extract_edges(self._faces)

    def _recompute_topology_from_cells(self, removed_cell_ids: Set[int], added_cells: List[MeshCell]):
        """Recomputes faces and edges from cells after changes."""
        from compgeom.mesh.mesh_topology import MeshTopology

        self._faces = MeshTopology.extract_faces(self._cells)
        self._edges = MeshTopology.extract_edges(self._faces)

    @property
    def vertices(self) -> List[Union[Point2D, Point3D]]:
        """Returns the list of points of the nodes."""
        return [node.point for node in self._nodes]

    def num_nodes(self) -> int:
        """Returns the number of nodes in the mesh."""
        return len(self._nodes)

    def num_edges(self) -> int:
        """Returns the number of edges in the mesh."""
        return len(self._edges)

    def num_faces(self) -> int:
        """Returns the number of faces in the mesh."""
        return len(self._faces)

    def num_cells(self) -> int:
        """Returns the number of cells in the mesh."""
        return len(self._cells)

    @property
    def centroid(self) -> Union[Point2D, Point3D]:
        """Returns the geometric centroid of the mesh nodes."""
        if not self._nodes:
            return Point2D(0, 0)
        points = self.vertices
        avg_x = sum(p.x for p in points) / len(points)
        avg_y = sum(p.y for p in points) / len(points)
        if isinstance(points[0], Point3D):
            avg_z = sum(p.z for p in points) / len(points)
            return Point3D(avg_x, avg_y, avg_z)
        return Point2D(avg_x, avg_y)

    def bounding_box(self) -> Tuple[Tuple[float, ...], Tuple[float, ...]]:
        """Returns the axis-aligned bounding box ((min_coords), (max_coords))."""
        if not self._nodes:
            return (0, 0), (0, 0)
        points = self.vertices
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        if isinstance(points[0], Point3D):
            min_z = min(p.z for p in points)
            max_z = max(p.z for p in points)
            return (min_x, min_y, min_z), (max_x, max_y, max_z)
        return (min_x, min_y), (max_x, max_y)

    def extract_topology(self) -> tuple:
        """Extracts topology based on mesh type.

        For surface mesh (has faces, no cells): extracts edges from faces.
        For volume mesh (has cells): extracts faces and edges from cells.

        Returns:
            Tuple of (edges, faces) lists.
        """
        from compgeom.mesh.mesh_topology import MeshTopology

        if self._cells:
            faces = MeshTopology.extract_faces(self._cells)
            edges = MeshTopology.extract_edges(faces)
            self._faces = faces
            self._edges = edges
        elif self._faces:
            edges = MeshTopology.extract_edges(self._faces)
            self._edges = edges

        return self._edges, self._faces

    def to_file(self, filename: str, **kwargs):
        """Exports the mesh to a file.

        Args:
            filename: Path to the output file (detects format from extension).
            **kwargs: Format-specific options (e.g., binary=True).
        """
        from compgeom.mesh.meshio import MeshExporter

        MeshExporter.write(filename, self, **kwargs)

    def reorder_nodes(self, new_order: List[int]):
        """Reorders the mesh nodes according to the given index list."""
        if len(new_order) != len(self._nodes):
            raise ValueError("New order must have the same length as current nodes")

        # 1. Reorder nodes
        old_nodes = {node.id: node for node in self._nodes}
        reordered_nodes = []
        old_to_new = {}
        for i, old_idx in enumerate(new_order):
            old_node = self._nodes[old_idx]
            reordered_nodes.append(replace(old_node, id=i))
            old_to_new[old_idx] = i
        self._nodes = reordered_nodes

        # 2. Update faces
        new_faces = []
        for face in self._faces:
            new_v = tuple(old_to_new[v_idx] for v_idx in face.v_indices)
            new_faces.append(replace(face, v_indices=new_v))
        self._faces = new_faces

        # 3. Update cells
        if self._cells:
            new_cells = []
            for cell in self._cells:
                new_v = tuple(old_to_new[v_idx] for v_idx in cell.v_indices)
                new_cells.append(replace(cell, v_indices=new_v))
            self._cells = new_cells

        # 4. Update edges
        if self._edges:
            new_edges = []
            for edge in self._edges:
                new_v = (old_to_new[edge.v_indices[0]], old_to_new[edge.v_indices[1]])
                new_edges.append(replace(edge, v_indices=new_v))
            self._edges = new_edges
