"""Mesh data structures and algorithms."""

from __future__ import annotations

from .surfmesh.trimesh.delaunay_triangulation import (
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
from .surfmesh.trimesh.mesh_refinement import TriMeshRefiner
from .mesh_reordering import CuthillMcKee
from .mesh_transfer import MeshTransfer
from .surfmesh.quadmesh.simple_tri2quads import TriangleToQuadConverter
from .polymesh.voronoi_diagram import VoronoiDiagram
from .volmesh.voxelmesh.voxelization import MeshVoxelizer
from .volmesh.tetmesh.delaunay_tetmesh import DelaunayTetMesher, triangulate as triangulate_3d

from .surfmesh.surf_mesh_repair import SurfMeshRepair
from .polymesh.point_winding_number import PolygonWinding, point_winding_number

__all__ = [
    "CuthillMcKee",
    "DTriangle",
    "DelaunayMesher",
    "DelaunayTetMesher",
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
    "SurfMeshRepair",
    "PolygonWinding",
    "point_winding_number",
    "euler_characteristic",
    "mesh_edges",
    "mesh_neighbors",
    "mesh_vertices",
    "triangle_neighbors",
    "triangulate",
    "triangulate_3d",
    "vertex_neighbors",
]
