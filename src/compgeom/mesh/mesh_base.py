"""Base classes for mesh data structures and topology."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Set, Tuple, Union

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.mesh_topology import MeshTopology


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

    def __init__(self, 
                 nodes: Optional[List[Union[MeshNode, Point2D, Point3D]]] = None, 
                 edges: Optional[List[MeshEdge]] = None, 
                 faces: Optional[List[MeshFace]] = None, 
                 cells: Optional[List[MeshCell]] = None):
        if nodes and not isinstance(nodes[0], MeshNode):
            nodes = [MeshNode(i, p) for i, p in enumerate(nodes)]
        elif nodes is None:
            nodes = []
        self._nodes = nodes
        self._edges = edges or []
        self._faces = faces or []
        self._cells = cells or []

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

    def to_file(self, filename: str, **kwargs):
        """Exports the mesh to a file.
        
        Args:
            filename: Path to the output file (detects format from extension).
            **kwargs: Format-specific options (e.g., binary=True).
        """
        from compgeom.mesh.meshio import MeshExporter
        MeshExporter.write(filename, self, **kwargs)
