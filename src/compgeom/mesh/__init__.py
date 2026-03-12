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
from .surfmesh.mesh_analysis import MeshAnalysis
from .surfmesh.mesh_processing import MeshProcessing
from .surfmesh.mesh_queries import MeshQueries
from .surfmesh.spatial_acceleration import AABBTree
from .surfmesh.mesh_decimation import MeshDecimator
from .surfmesh.curvature import MeshCurvature
from .surfmesh.remesher import IsotropicRemesher
from .polymesh.point_winding_number import PolygonWinding, point_winding_number
from .volmesh.marching_cubes import MarchingCubes

__all__ = [
    "AABBTree",
    "CuthillMcKee",
    "DTriangle",
    "DelaunayMesher",
    "DelaunayTetMesher",
    "DynamicDelaunay",
    "HexMesh",
    "IsotropicRemesher",
    "MarchingCubes",
    "build_topology",
    "constrained_delaunay_triangulation",
    "Mesh",
    "MeshAnalysis",
    "MeshColoring",
    "MeshCurvature",
    "MeshDecimator",
    "MeshImporter",
    "MeshExporter",
    "MeshProcessing",
    "MeshQueries",
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
