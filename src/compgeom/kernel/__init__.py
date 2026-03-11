from .geometry import *
from .math_utils import *

from .triangle import (
    area as triangle_area,
    circumcenter as triangle_circumcenter,
    incenter as triangle_incenter,
    inradius as triangle_inradius,
    contains_point, # Standard triangle point-in-tri test
    orientation,
    orientation_sign
)

from .line_segment import (
    intersect_lines,
    distance_to_point as dist_point_to_segment,
    contains_point as is_on_segment,
    intersect_proper as proper_segment_intersection,
    intersect_ray as ray_segment_intersection,
    midpoint as segment_midpoint,
    angle as segment_angle
)

from .circle import (
    incircle_det,
    incircle_sign,
    in_circle,
    from_two_points as get_circle_two_points,
    from_three_points as get_circle_three_points,
    area as circle_area,
    perimeter as circle_perimeter
)

from .quad import (
    area as quad_area,
    is_convex as is_convex_quad,
    split_to_triangles as split_quad_to_triangles,
    centroid as quad_centroid
)
