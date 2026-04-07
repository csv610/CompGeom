"""Polygon data structures and algorithms."""

from __future__ import annotations

from compgeom.polygon.convex_hull import ConvexHull
from compgeom.polygon.convex_hull_peeling import convex_hull_peeling
from compgeom.polygon.polygon import (
    Polygon,
    PolygonProperties,
    Triangle,
)
from compgeom.polygon.decomposer import (
    is_ear,
    triangulate_polygon,
    triangulate_polygon_with_holes,
    convex_decompose_polygon,
    monotone_decompose_polygon,
    visibility_decompose_polygon,
    trapezoidal_decompose_polygon,
    decompose_polygon,
    verify_polygon_decomposition,
    mesh_from_point_faces,
)
from compgeom.polygon.polygon_similarity import get_polygon_signature, polygons_are_similar
from compgeom.polygon.polygon_matching import reorder_to_match
from compgeom.polygon.polygon_simplification import resolve_self_intersections
from compgeom.polygon.polygon_polynomial import (
    approximate_polygon_polynomial,
    evaluate_polynomial,
    solve_linear_system,
)
from compgeom.polygon.polygon_generator import (
    generate_convex_polygon,
    generate_concave_polygon,
    generate_star_shaped_polygon,
    generate_sierpinski_triangle,
    generate_koch_snowflake,
    generate_dragon_curve,
    generate_de_rham_curve,
)
from compgeom.polygon.polygon_visibility import compute_visibility_polygon
from compgeom.polygon.polygon_guards import art_gallery_guards, guard_polygon
from compgeom.polygon.circle_packing import (
    pack_circles,
    optimal_radius,
    calculate_circle_packing_efficiency,
    visualize_circle_packing,
)
from compgeom.polygon.polygon_boolean import (
    polygon_union,
    polygon_intersection,
    polygon_difference,
    polygon_xor,
)
from compgeom.polygon.polygon_smoothing import (
    resample_polygon,
    fourier_smooth_polygon,
    mean_curvature_flow_polygon,
)
from compgeom.polygon.distance_map import solve_distance_map, visualize_distance_map_svg
from compgeom.polygon.medial_axis import sample_boundary_for_medial_axis, approximate_medial_axis
from compgeom.polygon.planar import (
    DCEL,
    DCELFace,
    DCELHalfEdge,
    DCELVertex,
)
from compgeom.polygon.polygon_utils import (
    ensure_ccw,
    ensure_cw,
    rotate_polygon,
    same_point,
    point_on_boundary,
    cleanup_polygon,
    segment_inside_boundaries,
)
from compgeom.polygon.polygon_metrics import (
    get_polygon_properties,
    is_polygon_convex,
    get_reflex_vertices,
    get_convex_diameter,
    is_point_in_polygon,
)
from compgeom.polygon.polygon_path import segment_inside_polygon, shortest_path_in_polygon
from compgeom.polygon.polygon_sampling import (
    get_perimeter_distances,
    sample_polygon_boundary,
    get_parametric_coordinate,
)
from compgeom.polygon.poly_square import poly_square
from compgeom.polygon.polygon_symmetry import get_polygon_moments, orient_polygon_for_symmetry

__all__ = [
    "approximate_medial_axis",
    "approximate_polygon_polynomial",
    "art_gallery_guards",
    "calculate_circle_packing_efficiency",
    "cleanup_polygon",
    "compute_visibility_polygon",
    "convex_decompose_polygon",
    "convex_hull_peeling",
    "ConvexHull",
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
    "decompose_polygon",
    "ensure_ccw",
    "ensure_cw",
    "evaluate_polynomial",
    "fourier_smooth_polygon",
    "generate_concave_polygon",
    "generate_convex_polygon",
    "generate_de_rham_curve",
    "generate_dragon_curve",
    "generate_koch_snowflake",
    "generate_sierpinski_triangle",
    "generate_star_shaped_polygon",
    "get_convex_diameter",
    "get_parametric_coordinate",
    "get_perimeter_distances",
    "get_polygon_moments",
    "get_polygon_properties",
    "get_polygon_signature",
    "get_reflex_vertices",
    "guard_polygon",
    "is_ear",
    "is_point_in_polygon",
    "is_polygon_convex",
    "mean_curvature_flow_polygon",
    "mesh_from_point_faces",
    "monotone_decompose_polygon",
    "optimal_radius",
    "pack_circles",
    "Polygon",
    "polygon_difference",
    "polygon_intersection",
    "PolygonProperties",
    "polygons_are_similar",
    "polygon_union",
    "polygon_xor",
    "poly_square",
    "reorder_to_match",
    "resolve_self_intersections",
    "resample_polygon",
    "rotate_polygon",
    "same_point",
    "sample_boundary_for_medial_axis",
    "sample_polygon_boundary",
    "segment_inside_boundaries",
    "segment_inside_polygon",
    "shortest_path_in_polygon",
    "solve_distance_map",
    "solve_linear_system",
    "trapezoidal_decompose_polygon",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
    "Triangle",
    "verify_polygon_decomposition",
    "visibility_decompose_polygon",
    "visualize_circle_packing",
    "visualize_distance_map_svg",
]
