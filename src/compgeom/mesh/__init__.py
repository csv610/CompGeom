"""Mesh data structures and algorithms."""

from __future__ import annotations

from .delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    Triangle,
)
from .mesh import (
    HexMesh,
    Mesh,
    MeshTopology,
    QuadMesh,
    TetMesh,
    TriangleMesh,
    euler_characteristic,
    mesh_edges,
    mesh_neighbors,
    mesh_vertices,
    triangle_neighbors,
    vertex_neighbors,
)
from .mesh_coloring import MeshColoring
from .mesh_io import MeshIO, OBJFileHandler, OFFFileHandler, STLFileHandler
from .mesh_refinement import TriMeshRefiner
from .mesh_reordering import CuthillMcKee
from .mesh_transfer import MeshTransfer
from .quadmesh.simple_tri2quads import TriangleToQuadConverter
from .triangulation import VoronoiDiagram
from .voxelization import MeshVoxelizer

__all__ = [
    "CuthillMcKee",
    "DTriangle",
    "DelaunayMesher",
    "DynamicDelaunay",
    "HexMesh",
    "Mesh",
    "MeshColoring",
    "MeshIO",
    "MeshTriangle",
    "MeshTopology",
    "MeshTransfer",
    "MeshVoxelizer",
    "OBJFileHandler",
    "OFFFileHandler",
    "STLFileHandler",
    "QuadMesh",
    "TetMesh",
    "TriMeshRefiner",
    "TriangleMesh",
    "TriangleToQuadConverter",
    "Triangle",
    "VoronoiDiagram",
    "euler_characteristic",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "vertex_neighbors",
]
