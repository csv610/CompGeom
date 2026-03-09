"""Mesh data structures and algorithms."""

from __future__ import annotations

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
from .mesh_io import OBJFileHandler
from .mesh_coloring import MeshColoring
from .mesh_refinement import TriMeshRefiner
from .mesh_reordering import CuthillMcKee
from .mesh_transfer import MeshTransfer
from .voxelization import MeshVoxelizer
from .quadmesh.simple_tri2quads_cli import TriangleToQuadConverter
from .triangulation import (
    DynamicDelaunay,
    constrained_delaunay_triangulation,
    build_topology,
    delaunay_flip,
    get_circle_boundary,
    get_square_boundary,
    get_voronoi_cells,
    triangulate,
)

__all__ = [
    "CuthillMcKee",
    "DynamicDelaunay",
    "HexMesh",
    "Mesh",
    "MeshColoring",
    "MeshTopology",
    "MeshTransfer",
    "MeshVoxelizer",
    "OBJFileHandler",
    "QuadMesh",
    "TetMesh",
    "TriMeshRefiner",
    "TriangleMesh",
    "TriangleToQuadConverter",
    "build_topology",
    "constrained_delaunay_triangulation",
    "delaunay_flip",
    "euler_characteristic",
    "get_circle_boundary",
    "get_square_boundary",
    "get_voronoi_cells",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "triangulate",
    "vertex_neighbors",
]
