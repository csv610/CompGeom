from .box import find_largest_empty_oriented_box
from .closest_pair import (
    closest_pair,
    closest_pair_divide_and_conquer,
    closest_pair_grid_based,
)
from compgeom.kernel import distance


class ClosestPair:
    @staticmethod
    def divide_and_conquer(points):
        return closest_pair_divide_and_conquer(points)

    @staticmethod
    def grid_based_massive(points, sample_size=10):
        points_list = list(points)
        return closest_pair_grid_based(iter(points_list), sample_size=sample_size)


class LargestEmptyCircle:
    @staticmethod
    def find(points):
        return find_largest_empty_circle(points)


class LargestEmptyOrientedBox:
    @staticmethod
    def find(points):
        return find_largest_empty_oriented_box(points)


class LargestEmptyOrientedEllipse:
    @staticmethod
    def find(points):
        return find_largest_empty_oriented_ellipse(points)


class LargestEmptyOrientedEllipsoid:
    @staticmethod
    def find(points):
        return find_largest_empty_oriented_ellipsoid(points)


class LargestEmptyOrientedRectangle:
    @staticmethod
    def find(points):
        return find_largest_empty_oriented_rectangle(points)


class LargestEmptySphere:
    @staticmethod
    def find(points):
        return find_largest_empty_sphere(points)


from .ellipse import find_largest_empty_oriented_ellipse
from .ellipsoid import find_largest_empty_oriented_ellipsoid
from .largest_empty_circle import (
    find_largest_empty_circle,
    visualize_largest_empty_circle,
)
from .largest_empty_sphere import find_largest_empty_sphere
from .minkowski_sum import minkowski_sum
from .rectangle import find_largest_empty_oriented_rectangle
from .utils import (
    do_intersect,
    farthest_pair,
    get_circle_three_points,
    get_circle_two_points,
    support,
    welzl,
)

__all__ = [
    "find_largest_empty_oriented_box",
    "closest_pair_divide_and_conquer",
    "closest_pair_grid_based",
    "ClosestPair",
    "distance",
    "find_largest_empty_oriented_ellipse",
    "find_largest_empty_oriented_ellipsoid",
    "find_largest_empty_circle",
    "visualize_largest_empty_circle",
    "find_largest_empty_sphere",
    "find_largest_empty_oriented_rectangle",
    "LargestEmptyCircle",
    "LargestEmptyOrientedBox",
    "LargestEmptyOrientedEllipse",
    "LargestEmptyOrientedEllipsoid",
    "LargestEmptyOrientedRectangle",
    "LargestEmptySphere",
    "closest_pair",
    "do_intersect",
    "farthest_pair",
    "get_circle_three_points",
    "get_circle_two_points",
    "minkowski_sum",
    "support",
    "welzl",
]
