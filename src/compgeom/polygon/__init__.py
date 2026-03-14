"""Polygon data structures and algorithms."""

from __future__ import annotations

from .convex_hull import ConvexHullGenerator, GrahamScan, MonotoneChain, QuickHull, Chan
from .polygon import (
    Polygon,
    PolygonProperties,
    get_convex_diameter,
    get_polygon_properties,
    get_reflex_vertices,
    get_triangulation_with_diagonals,
    hertel_mehlhorn,
    is_convex,
    is_ear,
    is_point_in_polygon,
    shortest_path_in_polygon,
    triangulate_polygon,
    triangulate_polygon_with_holes,
)
from .polygon_decomposer import PolygonDecomposer
from .polygon_similarity import are_similar
from .polygon_matching import reorder_to_match
from .polygon_simplification import resolve_self_intersections as make_simple
from .polygon_polynomial import approximate_polynomials
from .polygon_generator import (
    PolygonGenerator,
    generate_points_in_triangle,
    generate_random_convex_polygon,
    generate_simple_polygon,
)
from .polygon_visibility import polygon_kernel, visibility_polygon
from .polygon_guards import PolygonGuards, guard_polygon, solve_art_gallery
from .circle_packing import CirclePacker
from .polygon_smoothing import PolygonalMeanCurvatureFlow, fourier_smooth
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
    "ConvexHullGenerator",
    "GrahamScan",
    "MonotoneChain",
    "QuickHull",
    "Chan",
    "DistanceMapSolver",
    "PolygonDecomposer",
    "PolygonalMeanCurvatureFlow",
    "fourier_smooth",
    "PolygonGenerator",
    "PolygonGuards",
    "Polygon",
    "PolygonProperties",
    "approximate_medial_axis",
    "approximate_polynomials",
    "are_similar",
    "reorder_to_match",
    "make_simple",
    "build_polygon_dcel",
    "generate_points_in_triangle",
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "get_convex_diameter",
    "get_polygon_properties",
    "get_reflex_vertices",
    "get_triangulation_with_diagonals",
    "guard_polygon",
    "hertel_mehlhorn",
    "is_convex",
    "is_ear",
    "is_point_in_polygon",
    "locate_face",
    "polygon_kernel",
    "shortest_path_in_polygon",
    "solve_art_gallery",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
    "visibility_polygon",
]
