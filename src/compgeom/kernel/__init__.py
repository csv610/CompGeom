from compgeom.kernel.geometry import *
from compgeom.kernel.math_utils import *

from compgeom.kernel.triangle import Triangle2D, Triangle3D, area as triangle_area, contains_point as triangle_contains_point
from compgeom.kernel.line_segment import LineSegment, intersect_lines, intersect_proper as proper_segment_intersection, intersect_ray as ray_segment_intersection
from compgeom.kernel.circle import Circle2D, in_circle, area as circle_area, perimeter as circle_perimeter
from compgeom.kernel.quad import split_to_triangles as split_quad_to_triangles, centroid as quad_centroid
from compgeom.kernel.tetrahedron import Tetrahedron
from compgeom.kernel.hexahedron import Hexahedron
from compgeom.kernel.sphere import Sphere, in_sphere
from compgeom.kernel.plane import Plane
from compgeom.kernel.ray import Ray
from compgeom.kernel.polygon import Polygon2D
from compgeom.kernel.aabb import AABB2D, AABB3D
from compgeom.kernel.transformation import Transformation

# Intersection API
from compgeom.intersect import (
    tri_tri_intersect,
    tri_tetra_intersect,
    tri_hex_intersect,
    intersect_segments_2d,
    intersect_proper_2d,
    ray_segment_intersect_2d,
    ray_triangle_intersect,
    ray_sphere_intersect,
    ray_aabb_intersect_3d,
    ray_mesh_intersect,
    mesh_mesh_intersect
)
