"""Mesh data structures and algorithms."""

from __future__ import annotations

from compgeom.mesh.surface.trimesh.delaunay_triangulation import (
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
    ConformingHexMesher,
    Mesh,
    MeshAffineTransform,
    MeshGeometry,
    MeshCell,
    MeshEdge,
    MeshFace,
    MeshNode,
    MeshTopology,
    mesh_neighbors,
    PolygonMesh,
    QuadMesh,
    SurfaceMesh,
    TetMesh,
    TriMesh,
)
from compgeom.mesh.edge_mesh import EdgeMesh
from compgeom.mesh.algorithms.mesh_coloring import MeshColoring
from compgeom.mesh.meshio import (
    MeshImporter,
    MeshExporter,
    OBJFileHandler,
    OFFFileHandler,
    STLFileHandler,
    PLYFileHandler,
    from_file,
    to_file,
)
from compgeom.mesh.surface.trimesh.mesh_refinement import TriMeshRefiner
from compgeom.mesh.algorithms.mesh_reordering import CuthillMcKee, MeshReorderer
from compgeom.mesh.algorithms.mesh_transfer import MeshTransfer
from compgeom.mesh.surface.quadmesh.simple_tri2quads import TriangleToQuadConverter
from compgeom.mesh.polygon.voronoi_diagram import VoronoiDiagram
from compgeom.mesh.volume.voxelmesh.voxelization import MeshVoxelizer
from compgeom.mesh.volume.tetmesh.delaunay_tetmesh import DelaunayTetMesher, triangulate as triangulate_3d
from compgeom.mesh.volume.marching_tetrahedra import MarchingTetrahedra
from compgeom.mesh.algorithms.coacd import CoACD
from compgeom.mesh.algorithms.dec import DEC
from compgeom.mesh.algorithms.discrete_morse import DiscreteMorse
from compgeom.mesh.algorithms.hodge_theory import HodgeDecomposition
from compgeom.mesh.algorithms.matroid import (
    Matroid,
    GraphicMatroid,
    MeshGraphicMatroid,
    TransversalMatroid,
    create_graphic_matroid,
)
from compgeom.mesh.surface.trimesh.intrinsic_triangulation import IntrinsicTriangulation
from compgeom.mesh.surface.trimesh.non_obtuse_triangulation import NonObtuseTriangulator
from compgeom.mesh.surface.trimesh.binary_image_triangulation import BinaryImageTriangulation
from compgeom.mesh.surface.parameterization_lscm import LSCMParameterizer
from compgeom.mesh.surface.ricci_flow import RicciFlow
from compgeom.mesh.surface.conformal_equivalence import DiscreteConformalEquivalence
from compgeom.mesh.surface.quasi_conformal import QuasiConformalMap
from compgeom.mesh.surface.arap import ARAPMapper, as_rigid_as_possible
from compgeom.mesh.surface.circle_packing import CirclePacking, ThurstonCirclePacking, discrete_circle_packing
from compgeom.mesh.surface.tutte_embedding import (
    TutteEmbedding,
    CotangentLaplacian,
    tutte_embedding,
    cotangent_laplacian,
)
from compgeom.mesh.surface.conformal_deformation import (
    ConformalDeformation,
    HarmonicConformalDeformation,
    conformal_deform,
    conformal_deform_rots,
)
from compgeom.mesh.surface.abf_plus_plus import ABFPlusPlus, ABFParameterization, abf_plus_plus
from compgeom.mesh.surface.yamabe_flow import DiscreteYamabeFlow, YamabeFlowParameterization, yamabe_flow
from compgeom.mesh.surface.conformal_registration import (
    ConformalShapeRegistration,
    FunctionalMap,
    ConformalMorph,
    register_conformal_shapes,
    conformal_morph,
)
from compgeom.mesh.surface.mean_value_coordinates import (
    MeanValueCoordinates,
    MeanValueEmbedding,
    MeanValueLaplacian,
    mean_value_coordinates,
)
from compgeom.mesh.surface.levi_civita_connection import (
    LeviCivitaConnection,
    SpinConnection,
    parallel_transport,
)
from compgeom.mesh.surface.non_euclidean import (
    SphericalConformalMap,
    PoincareDiskEmbedding,
    stereographic_forward,
    stereographic_inverse,
    poincare_disk_embedding,
    hyperbolic_distance,
    hemisphere_embedding,
    poincare_disk_map,
)

from compgeom.mesh.surface.mesh_analysis import MeshAnalysis
from compgeom.mesh.surface.processing import *
from compgeom.mesh.surface.repair import *
from compgeom.mesh.surface.mesh_queries import MeshQueries
from compgeom.mesh.surface.spatial_acceleration import AABBTree
from compgeom.mesh.surface.mesh_decimation import MeshDecimator
from compgeom.mesh.surface.halfedge_mesh import HalfEdgeMesh
from compgeom.mesh.surface.mesh_quality import MeshQuality
from compgeom.mesh.surface.curvature import MeshCurvature
from compgeom.mesh.surface.surface_evaluator import SurfaceEvaluator, SphereEvaluator
from compgeom.mesh.surface.manifold_repair import ManifoldValidator, ManifoldFixer
from compgeom.mesh.surface.remesher import IsotropicRemesher, AdaptiveRemesher
from compgeom.mesh.surface.alpha_shapes import AlphaShape
from compgeom.mesh.surface.parameterization import MeshParameterization
from compgeom.mesh.surface.convex_hull import ConvexHull3D
from compgeom.mesh.surface.bounding_volumes import BoundingVolumes
from compgeom.mesh.surface.registration import MeshRegistration
from compgeom.mesh.surface.mesh_validation import MeshValidation
from compgeom.mesh.polygon.point_winding_number import PolygonWinding, point_winding_number
from compgeom.mesh.polygon.sweep_line import SweepLine
from compgeom.mesh.polygon.polygon_triangulation import PolygonTriangulation
from compgeom.mesh.polygon.minkowski import MinkowskiSum
from compgeom.mesh.polygon.vlsi_layout import VLSILayout
from compgeom.mesh.volume.marching_cubes import MarchingCubes
from compgeom.mesh.volume.volume_quality import TetMeshQuality

from compgeom.mesh.surface.mesh_booleans import MeshBooleans

from compgeom.mesh.polygon.polygon_booleans import PolygonBooleans


__all__ = [
    "AABBTree",
    "AlphaShape",
    "AdaptiveRemesher",
    "bilateral_smoothing",
    "BinaryImageTriangulation",
    "BoundingVolumes",
    "catmull_clark",
    "ConvexHull3D",
    "CuthillMcKee",
    "CoACD",
    "DEC",
    "DTriangle",
    "DelaunayMesher",
    "DelaunayTetMesher",
    "DiscreteConformalEquivalence",
    "DiscreteMorse",
    "DynamicDelaunay",
    "EdgeMesh",
    "fill_holes",
    "fix_normals",
    "flip_normals",
    "HalfEdgeMesh",
    "HexMesh",
    "HodgeDecomposition",
    "GraphicMatroid",
    "MeshGraphicMatroid",
    "create_graphic_matroid",
    "IsotropicRemesher",
    "IntrinsicTriangulation",
    "laplacian_smoothing",
    "loop_subdivision",
    "LSCMParameterizer",
    "ManifoldValidator",
    "ManifoldFixer",
    "MarchingCubes",
    "MarchingTetrahedra",
    "mesh_clipping",
    "mesh_offset",
    "MinkowskiSum",
    "NonObtuseTriangulator",
    "orient_normals_outward",
    "PolygonBooleans",
    "PolygonTriangulation",
    "QuasiConformalMap",
    "ARAPMapper",
    "as_rigid_as_possible",
    "CirclePacking",
    "ThurstonCirclePacking",
    "discrete_circle_packing",
    "CotangentLaplacian",
    "TutteEmbedding",
    "tutte_embedding",
    "cotangent_laplacian",
    "ConformalDeformation",
    "HarmonicConformalDeformation",
    "conformal_deform",
    "conformal_deform_rots",
    "ABFPlusPlus",
    "ABFParameterization",
    "abf_plus_plus",
    "DiscreteYamabeFlow",
    "yamabe_flow",
    "ConformalShapeRegistration",
    "FunctionalMap",
    "ConformalMorph",
    "register_conformal_shapes",
    "conformal_morph",
    "MeanValueCoordinates",
    "MeanValueEmbedding",
    "MeanValueLaplacian",
    "mean_value_coordinates",
    "LeviCivitaConnection",
    "SpinConnection",
    "parallel_transport",
    "SphericalConformalMap",
    "PoincareDiskEmbedding",
    "stereographic_forward",
    "stereographic_inverse",
    "poincare_disk_embedding",
    "hyperbolic_distance",
    "hemisphere_embedding",
    "poincare_disk_map",
    "repair",
    "remove_degenerate_faces",
    "remove_duplicate_faces",
    "remove_duplicate_points",
    "remove_isolated_vertices",
    "remove_non_manifold_faces",
    "remove_non_manifold_vertices",
    "remove_self_intersections",
    "remove_small_components",
    "RicciFlow",
    "SweepLine",
    "taubin_smoothing",
    "VLSILayout",
    "build_topology",
    "constrained_delaunay_triangulation",
    "ConformingHexMesher",
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
    "MeshQueries",
    "MeshReorderer",
    "MeshTriangle",
    "MeshTopology",
    "mesh_neighbors",
    "MeshTransfer",
    "MeshVoxelizer",
    "OBJFileHandler",
    "OFFFileHandler",
    "STLFileHandler",
    "PLYFileHandler",
    "PolygonMesh",
    "PolygonWinding",
    "QuadMesh",
    "SurfaceMesh",
    "SurfaceEvaluator",
    "SphereEvaluator",
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
