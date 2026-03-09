"""Shared geometry and algorithm package for the TriangleMesh project."""

from .geometry import EPSILON, Point
from .planar import DCEL, DCELFace, DCELHalfEdge, DCELVertex, build_polygon_dcel, locate_face
from .visualization import generate_svg_path, save_svg, save_png
from .rectangle_packing import RectanglePacker
from .voxelization import MeshVoxelizer
from .mesh_io import OBJFileHandler
from .sequences import DavenportSchinzel
from .circle_packing import CirclePacker
from .shapes import (
    Circle,
    Cube,
    Cuboid,
    Hexahedron,
    LineSegment,
    Plane,
    Ray,
    Rectangle,
    Shape,
    Shape2D,
    Shape3D,
    Sphere,
    Square,
    Tetrahedron,
    Triangle,
)
from .proximity import LargestEmptyCircle
from .mesh import (
    HexMesh,
    Mesh,
    MeshTopology,
    QuadMesh,
    TetMesh,
    TriangleMesh,
)
from .mesh_refinement import TriMeshRefiner
from .mesh_coloring import MeshColoring

__all__ = [
    "Circle",
    "CirclePacker",
    "Cube",
    "Cuboid",
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
    "DavenportSchinzel",
    "EPSILON",
    "HexMesh",
    "Hexahedron",
    "LargestEmptyCircle",
    "LineSegment",
    "Mesh",
    "MeshColoring",
    "MeshTopology",
    "MeshVoxelizer",
    "OBJFileHandler",
    "Plane",
    "Point",
    "QuadMesh",
    "Ray",
    "Rectangle",
    "RectanglePacker",
    "Shape",
    "Shape2D",
    "Shape3D",
    "Sphere",
    "Square",
    "TetMesh",
    "Tetrahedron",
    "TriMeshRefiner",
    "Triangle",
    "TriangleMesh",
    "build_polygon_dcel",
    "generate_svg_path",
    "locate_face",
    "save_svg",
    "save_png",
]
