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
    MeshCell,
    MeshEdge,
    MeshFace,
    MeshNode,
    MeshTopology,
    PolygonMesh,
    QuadMesh,
    TetMesh,
    TriMesh,
)
from .edge_mesh import EdgeMesh
from .meshalgo.mesh_coloring import MeshColoring
from .meshio import MeshImporter, MeshExporter, OBJFileHandler, OFFFileHandler, STLFileHandler, PLYFileHandler, from_file, to_file
from .surfmesh.trimesh.mesh_refinement import TriMeshRefiner
from .meshalgo.mesh_reordering import CuthillMcKee
from .meshalgo.mesh_transfer import MeshTransfer
from .surfmesh.quadmesh.simple_tri2quads import TriangleToQuadConverter
from .polymesh.voronoi_diagram import VoronoiDiagram
from .volmesh.voxelmesh.voxelization import MeshVoxelizer
from .volmesh.tetmesh.delaunay_tetmesh import DelaunayTetMesher, triangulate as triangulate_3d

from .surfmesh.mesh_analysis import MeshAnalysis
from .surfmesh.mesh_processing import MeshProcessing
from .surfmesh.mesh_queries import MeshQueries
from .surfmesh.spatial_acceleration import AABBTree
from .surfmesh.mesh_decimation import MeshDecimator
from .surfmesh.halfedge_mesh import HalfEdgeMesh
from .surfmesh.mesh_quality import MeshQuality
from .surfmesh.curvature import MeshCurvature
from .surfmesh.remesher import IsotropicRemesher, AdaptiveRemesher
from .surfmesh.alpha_shapes import AlphaShape
from .surfmesh.parameterization import MeshParameterization
from .surfmesh.convex_hull import ConvexHull3D
from .surfmesh.bounding_volumes import BoundingVolumes
from .surfmesh.registration import MeshRegistration
from .surfmesh.mesh_validation import MeshValidation
from .polymesh.point_winding_number import PolygonWinding, point_winding_number
from .polymesh.sweep_line import SweepLine
from .polymesh.polygon_triangulation import PolygonTriangulation
from .polymesh.minkowski import MinkowskiSum
from .polymesh.vlsi_layout import VLSILayout
from .volmesh.marching_cubes import MarchingCubes
from .volmesh.volmesh_quality import TetMeshQuality

from .surfmesh.mesh_booleans import MeshBooleans

from .polymesh.polygon_booleans import PolygonBooleans

__all__ = [
    "AABBTree",
    "AlphaShape",
    "AdaptiveRemesher",
    "BoundingVolumes",
    "ConvexHull3D",
    "CuthillMcKee",
    "DTriangle",
    "DelaunayMesher",
    "DelaunayTetMesher",
    "DynamicDelaunay",
    "EdgeMesh",
    "HalfEdgeMesh",
    "HexMesh",
    "IsotropicRemesher",
    "MarchingCubes",
    "MinkowskiSum",
    "PolygonBooleans",
    "PolygonTriangulation",
    "SweepLine",
    "VLSILayout",
    "build_topology",
    "constrained_delaunay_triangulation",
    "Mesh",
    "MeshCell",
    "MeshEdge",
    "MeshFace",
    "MeshNode",
    "MeshAnalysis",
    "MeshBooleans",
    "MeshColoring",
    "MeshCurvature",
    "MeshDecimator",
    "MeshParameterization",
    "MeshRegistration",
    "MeshValidation",
    "from_file",
    "to_file",
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
    "PLYFileHandler",
    "PolygonMesh",
    "PolygonWinding",
    "QuadMesh",
    "TetMesh",
    "TetMeshQuality",
    "TriMeshRefiner",
    "TriMesh",
    "TriangleToQuadConverter",
    "Triangle",
    "VoronoiDiagram",
    "point_winding_number",
    "triangulate",
    "triangulate_3d",
]
