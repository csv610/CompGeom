"""Polygon data structures and algorithms."""

from __future__ import annotations

from .polygon import (
    generate_points_in_triangle,
    generate_random_convex_polygon,
    generate_simple_polygon,
    get_convex_diameter,
    get_polygon_properties,
    get_reflex_vertices,
    get_triangulation_with_diagonals,
    graham_scan,
    hertel_mehlhorn,
    is_convex,
    is_ear,
    is_point_in_polygon,
    monotone_chain,
    shortest_path_in_polygon,
    solve_art_gallery,
    triangulate_polygon,
    triangulate_polygon_with_holes,
    visibility_polygon,
)
from .convex_decomposition import ConvexDecomposer
from .circle_packing import CirclePacker
from .polygon_smoothing import PolygonalMeanCurvatureFlow
from .distance_map import DistanceMapSolver
from .medial_axis import approximate_medial_axis
from .planar import (
    DCEL,
    DCELFace,
    DCELHalfEdge,
    DCELVertex,
    build_polygon_dcel,
    locate_face,
)

__all__ = [
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
    "CirclePacker",
    "ConvexDecomposer",
    "DistanceMapSolver",
    "PolygonalMeanCurvatureFlow",
    "approximate_medial_axis",
    "build_polygon_dcel",
    "generate_points_in_triangle",
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "get_convex_diameter",
    "get_polygon_properties",
    "get_reflex_vertices",
    "get_triangulation_with_diagonals",
    "graham_scan",
    "hertel_mehlhorn",
    "is_convex",
    "is_ear",
    "is_point_in_polygon",
    "locate_face",
    "monotone_chain",
    "shortest_path_in_polygon",
    "solve_art_gallery",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
    "visibility_polygon",
]
