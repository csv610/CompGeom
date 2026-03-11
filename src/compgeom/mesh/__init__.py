"""Mesh data structures and algorithms."""

from __future__ import annotations

from .trimesh.delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    Triangle,
    build_topology,
    constrained_delaunay_triangulation,
    triangulate,
)
from .mesh import (
    HexMesh,
    Mesh,
    MeshTopology,
    PolygonMesh,
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
from .mesh_io import MeshImporter, MeshExporter, OBJFileHandler, OFFFileHandler, STLFileHandler
from .trimesh.mesh_refinement import TriMeshRefiner
from .mesh_reordering import CuthillMcKee
from .mesh_transfer import MeshTransfer
from .quadmesh.simple_tri2quads import TriangleToQuadConverter
from .polymesh.voronoi_diagram import VoronoiDiagram
from .voxelmesh.voxelization import MeshVoxelizer

__all__ = [
    "CuthillMcKee",
    "DTriangle",
    "DelaunayMesher",
    "DynamicDelaunay",
    "HexMesh",
    "build_topology",
    "constrained_delaunay_triangulation",
    "Mesh",
    "MeshColoring",
    "MeshImporter",
    "MeshExporter",
    "MeshTriangle",
    "MeshTopology",
    "MeshTransfer",
    "MeshVoxelizer",
    "OBJFileHandler",
    "OFFFileHandler",
    "STLFileHandler",
    "PolygonMesh",
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
    "triangulate",
    "vertex_neighbors",
]
