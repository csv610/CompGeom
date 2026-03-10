"""Mesh data structures and algorithms."""

from __future__ import annotations

from .delaunay_triangulation import (
    DelaunayMesher,
    DynamicDelaunay,
    build_topology,
    constrained_delaunay_triangulation,
    delaunay_flip,
    get_nondelaunay_triangles,
    is_delaunay,
    triangulate,
    triangulate_divide_and_conquer,
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
from .mesh_io import OBJFileHandler
from .mesh_refinement import TriMeshRefiner
from .mesh_reordering import CuthillMcKee
from .mesh_transfer import MeshTransfer
from .quadmesh.simple_tri2quads import TriangleToQuadConverter
from .triangulation import (
    VoronoiDiagram,
    get_circle_boundary,
    get_square_boundary,
    get_voronoi_cells,
)
from .voxelization import MeshVoxelizer

__all__ = [
    "CuthillMcKee",
    "DelaunayMesher",
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
    "VoronoiDiagram",
    "build_topology",
    "constrained_delaunay_triangulation",
    "delaunay_flip",
    "euler_characteristic",
    "get_circle_boundary",
    "get_nondelaunay_triangles",
    "get_square_boundary",
    "get_voronoi_cells",
    "is_delaunay",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "triangulate",
    "triangulate_divide_and_conquer",
    "vertex_neighbors",
]
