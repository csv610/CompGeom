"""Mesh data structures and algorithms."""

from __future__ import annotations

from compgeom.mesh.surfmesh.trimesh.delaunay_triangulation import (
    DTriangle,
    DelaunayMesher,
    DynamicDelaunay,
    MeshTriangle,
    Triangle,
    build_topology,
    constrained_delaunay_triangulation,
    triangulate,
)
from compgeom.mesh.mesh import (
    HexMesh,
    Mesh,
    MeshAffineTransform,
    MeshGeometry,
    MeshCell,
    MeshEdge,
    MeshFace,
    MeshNode,
    MeshTopology,
    PolygonMesh,
    QuadMesh,
    TetMesh,
    TriMesh
)
from compgeom.mesh.edge_mesh import EdgeMesh
from compgeom.mesh.meshalgo.mesh_coloring import MeshColoring
from compgeom.mesh.meshio import MeshImporter, MeshExporter, OBJFileHandler, OFFFileHandler, STLFileHandler, PLYFileHandler, from_file, to_file
from compgeom.mesh.surfmesh.trimesh.mesh_refinement import TriMeshRefiner
from compgeom.mesh.meshalgo.mesh_reordering import CuthillMcKee, MeshReorderer
from compgeom.mesh.meshalgo.mesh_transfer import MeshTransfer
from compgeom.mesh.surfmesh.quadmesh.simple_tri2quads import TriangleToQuadConverter
from compgeom.mesh.polymesh.voronoi_diagram import VoronoiDiagram
from compgeom.mesh.volmesh.voxelmesh.voxelization import MeshVoxelizer
from compgeom.mesh.volmesh.tetmesh.delaunay_tetmesh import DelaunayTetMesher, triangulate as triangulate_3d

from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
from compgeom.mesh.surfmesh.mesh_processing import MeshProcessing
from compgeom.mesh.surfmesh.mesh_queries import MeshQueries
from compgeom.mesh.surfmesh.spatial_acceleration import AABBTree
from compgeom.mesh.surfmesh.mesh_decimation import MeshDecimator
from compgeom.mesh.surfmesh.halfedge_mesh import HalfEdgeMesh
from compgeom.mesh.surfmesh.mesh_quality import MeshQuality
from compgeom.mesh.surfmesh.curvature import MeshCurvature
from compgeom.mesh.surfmesh.remesher import IsotropicRemesher, AdaptiveRemesher
from compgeom.mesh.surfmesh.alpha_shapes import AlphaShape
from compgeom.mesh.surfmesh.parameterization import MeshParameterization
from compgeom.mesh.surfmesh.convex_hull import ConvexHull3D
from compgeom.mesh.surfmesh.bounding_volumes import BoundingVolumes
from compgeom.mesh.surfmesh.registration import MeshRegistration
from compgeom.mesh.surfmesh.mesh_validation import MeshValidation
from compgeom.mesh.polymesh.point_winding_number import PolygonWinding, point_winding_number
from compgeom.mesh.polymesh.sweep_line import SweepLine
from compgeom.mesh.polymesh.polygon_triangulation import PolygonTriangulation
from compgeom.mesh.polymesh.minkowski import MinkowskiSum
from compgeom.mesh.polymesh.vlsi_layout import VLSILayout
from compgeom.mesh.volmesh.marching_cubes import MarchingCubes
from compgeom.mesh.volmesh.volmesh_quality import TetMeshQuality

from compgeom.mesh.surfmesh.mesh_booleans import MeshBooleans

from compgeom.mesh.polymesh.polygon_booleans import PolygonBooleans

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
    "MeshAffineTransform",
    "MeshGeometry",
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
    "MeshReorderer",
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
