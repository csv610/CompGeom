"""Base classes for mesh data structures and topology."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Set, Tuple, Union

from ..kernel import Point2D, Point3D
from .mesh_topology import MeshTopology


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


@dataclass(frozen=True)
class MeshCell:
    """A volumetric cell in the mesh (e.g., tetrahedron, hexahedron)."""
    id: int
    v_indices: Tuple[int, ...]
    attributes: Dict = field(default_factory=dict)


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
