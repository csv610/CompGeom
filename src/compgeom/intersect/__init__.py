from compgeom.intersect.primitive import (
    tri_tri_intersect,
    tri_tri_coplanar_intersect,
    tri_tetra_intersect,
    tri_hex_intersect,
    box_box_intersect_2d,
    box_box_intersect_3d,
)
from compgeom.intersect.line import (
    intersect_segments_2d,
    intersect_proper_2d,
    ray_segment_intersect_2d,
    segment_plane_intersect_3d,
)
from compgeom.intersect.ray import (
    ray_triangle_intersect,
    ray_sphere_intersect,
    ray_aabb_intersect_3d,
    ray_plane_intersect,
)
from compgeom.intersect.mesh import (
    ray_mesh_intersect,
    mesh_mesh_intersect,
)
