"""Shared geometry and algorithm package for the TriangleMesh project."""

from .geometry import EPSILON, Point
from .planar import DCEL, DCELFace, DCELHalfEdge, DCELVertex, build_polygon_dcel, locate_face
from .visualization import generate_svg_path, save_svg, save_png
from .rectangle_packing import RectanglePacker
from .voxelization import MeshVoxelizer
from .mesh_io import OBJFileHandler
from .sequences import DavenportSchinzel

__all__ = [
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
    "DavenportSchinzel",
    "EPSILON",
    "Point",
    "MeshVoxelizer",
    "OBJFileHandler",
    "RectanglePacker",
    "build_polygon_dcel",
    "generate_svg_path",
    "locate_face",
    "save_svg",
    "save_png",
]
