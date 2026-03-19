from compgeom.kernel.geometry import *
from compgeom.kernel.math_utils import *

from compgeom.kernel.triangle import (
    area as triangle_area,
    circumcenter as triangle_circumcenter,
    incenter as triangle_incenter,
    inradius as triangle_inradius,
    contains_point, contains_point as triangle_contains_point,
    barycentric_coords as triangle_barycentric_coords,
    orientation, orientation as triangle_orientation,
    orientation_sign, orientation_sign as triangle_orientation_sign
)

from compgeom.kernel.line_segment import (
    intersect_lines,
    distance_to_point as dist_point_to_segment,
    contains_point as is_on_segment,
    intersect_proper as proper_segment_intersection,
    intersect_ray as ray_segment_intersection,
    midpoint as segment_midpoint,
    angle as segment_angle
)

from compgeom.kernel.circle import (
    Circle2D,
    common_tangents,
    tangents_from_point,
    incircle_det,
    incircle_sign,
    in_circle,
    robust_in_circle,
    from_two_points as circle_from_two_points,
    from_three_points as circle_from_three_points,
    area as circle_area,
    perimeter as circle_perimeter
)

from compgeom.kernel.quad import (
    area as quad_area,
    is_convex as is_convex_quad,
    split_to_triangles as split_quad_to_triangles,
    centroid as quad_centroid,
    min_circle as quad_min_circle,
    is_planar as is_planar_quad,
    is_cyclic as is_cyclic_quad,
    barycentric_coords as quad_barycentric_coords
)

from compgeom.kernel.tetrahedron import (
    orientation as tetra_orientation,
    orientation_sign as tetra_orientation_sign,
    volume as tetra_volume,
    contains_point as tetra_contains_point,
    barycentric_coords as tetra_barycentric_coords
)

from compgeom.kernel.hexahedron import (
    Hexahedron,
    centroid as hexa_centroid,
    volume as hexa_volume,
    is_convex as is_convex_hexa,
    min_sphere as hexa_min_sphere,
    barycentric_coords as hexa_barycentric_coords
)

from compgeom.kernel.sphere import (
    Sphere,
    insphere_det,
    insphere_sign,
    in_sphere,
    from_two_points as sphere_from_two_points,
    from_three_points as sphere_from_three_points,
    from_four_points as sphere_from_four_points
)

from compgeom.kernel.plane import (
    Plane
)

from compgeom.kernel.ray import (
    Ray
)

from compgeom.kernel.polygon import (
    Polygon2D
)

from compgeom.kernel.aabb import (
    AABB2D,
    AABB3D
)

from compgeom.kernel.transformation import (
    Transformation
)

get_circle_two_points = circle_from_two_points
get_circle_three_points = circle_from_three_points
