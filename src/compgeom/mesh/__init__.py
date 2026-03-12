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
from .surfmesh.halfedge_mesh import HalfEdgeMesh
from .surfmesh.mesh_quality import MeshQuality
from .surfmesh.curvature import MeshCurvature
from .surfmesh.remesher import IsotropicRemesher
from .surfmesh.alpha_shapes import AlphaShape
from .surfmesh.parameterization import MeshParameterization
from .surfmesh.convex_hull import ConvexHull3D
from .surfmesh.bounding_volumes import BoundingVolumes
from .surfmesh.registration import MeshRegistration
from .polymesh.point_winding_number import PolygonWinding, point_winding_number
from .volmesh.marching_cubes import MarchingCubes
from .volmesh.volmesh_quality import TetMeshQuality

from .surfmesh.mesh_booleans import MeshBooleans
from .surfmesh.geodesics import MeshGeodesics
from .mesh_io import MeshImporter, MeshExporter, OBJFileHandler, OFFFileHandler, STLFileHandler, PLYFileHandler

__all__ = [
    "AABBTree",
    "AlphaShape",
    "BoundingVolumes",
    "ConvexHull3D",
    "CuthillMcKee",
    "DTriangle",
    "DelaunayMesher",
    "DelaunayTetMesher",
    "DynamicDelaunay",
    "HalfEdgeMesh",
    "HexMesh",
    "IsotropicRemesher",
    "MarchingCubes",
    "build_topology",
    "constrained_delaunay_triangulation",
    "Mesh",
    "MeshAnalysis",
    "MeshBooleans",
    "MeshColoring",
    "MeshCurvature",
    "MeshDecimator",
    "MeshGeodesics",
    "MeshParameterization",
    "MeshRegistration",
    "MeshParameterization",

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
    "TriangleMesh",
    "TriangleToQuadConverter",
    "Triangle",
    "VoronoiDiagram",
    "SurfMeshRepair",
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

