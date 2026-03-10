"""Core polygon data structures."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence, Union

from ..geo_math.geometry import (
    Point,
    Point3D,
    is_on_segment,
)
from .polygon_utils import ensure_ccw, ensure_cw


@dataclass(frozen=True, slots=True)
class PolygonProperties:
    area: float
    centroid: Point
    orientation: str

@dataclass(frozen=True, slots=True)
class Polygon:
    vertices: tuple[Point, ...]

    def __init__(self, vertices: Sequence[Point]):
        object.__setattr__(self, "vertices", tuple(vertices))

    def __iter__(self):
        return iter(self.vertices)

    def __len__(self) -> int:
        return len(self.vertices)

    def __getitem__(self, index: int) -> Point:
        return self.vertices[index]

    def as_list(self) -> list[Point]:
        return list(self.vertices)

    def ensure_ccw(self) -> Polygon:
        return Polygon(ensure_ccw(self.as_list()))

    def ensure_cw(self) -> Polygon:
        return Polygon(ensure_cw(self.as_list()))

    def properties(self) -> PolygonProperties:
        from .polygon_metrics import get_polygon_properties

        area, centroid, orientation = get_polygon_properties(self.as_list())
        return PolygonProperties(area, centroid, orientation)

    def contains_point(self, point: Point) -> bool:
        polygon = self.vertices
        n = len(polygon)
        if n < 3:
            return False

        inside = False
        for i in range(n):
            start = polygon[i]
            end = polygon[(i + 1) % n]

            if is_on_segment(point, start, end):
                return True

            if ((start.y > point.y) != (end.y > point.y)) and (
                point.x < (end.x - start.x) * (point.y - start.y) / (end.y - start.y) + start.x
            ):
                inside = not inside

        return inside

    def _segment_inside(self, start: Point, end: Point) -> bool:
        from .polygon_path import segment_inside_polygon

        return segment_inside_polygon(self.as_list(), start, end)

    def visibility_polygon(self, viewpoint: Point) -> list[Point]:
        from .polygon_visibility import visibility_polygon

        return visibility_polygon(viewpoint, self.as_list())

    def kernel(self) -> list[Point]:
        from .polygon_visibility import polygon_kernel

        return polygon_kernel(self.as_list())

    def shortest_path(self, source: Point, target: Point) -> tuple[list[Point], float]:
        from .polygon_path import shortest_path_in_polygon

        return shortest_path_in_polygon(self.as_list(), source, target)

    def hertel_mehlhorn(self) -> tuple[list[list[int]], list[Point]]:
        from .polygon_decomposer import _hertel_mehlhorn

        return _hertel_mehlhorn(self.as_list())

    def is_convex(self) -> bool:
        from .polygon_metrics import is_convex

        return is_convex(self.as_list())

    def reflex_vertices(self) -> list[Point]:
        from .polygon_metrics import get_reflex_vertices

        return get_reflex_vertices(self.as_list())

    def convex_diameter(self) -> float:
        from .polygon_metrics import get_convex_diameter

        return get_convex_diameter(self.as_list())

    @classmethod
    def from_random_convex(
        cls,
        num_points: int = 10,
        x_range: tuple[float, float] = (0, 100),
        y_range: tuple[float, float] = (0, 100),
    ) -> Polygon:
        from .polygon_factory import random_convex_polygon

        return random_convex_polygon(num_points, x_range, y_range, polygon_cls=cls)

    @classmethod
    def from_simple_random(
        cls,
        n_points: int = 20,
        x_range: tuple[float, float] = (0, 100),
        y_range: tuple[float, float] = (0, 100),
    ) -> Polygon:
        from .polygon_factory import simple_polygon

        return simple_polygon(n_points, x_range, y_range, polygon_cls=cls)
def get_polygon_properties(polygon: list[Point]) -> tuple[float, Point, str]:
    from .polygon_metrics import get_polygon_properties as _get_polygon_properties

    return _get_polygon_properties(polygon)


def is_point_in_polygon(point: Point, polygon: list[Point]) -> bool:
    return Polygon(polygon).contains_point(point)


def is_ear(a: Point, b: Point, c: Point, polygon: list[Point]) -> bool:
    from .polygon_decomposer import _is_ear

    return _is_ear(a, b, c, polygon)


def triangulate_polygon(polygon: list[Point]) -> tuple[list[tuple[int, int, int]], list[Point]]:
    from .polygon_decomposer import _ear_clip

    triangles, _, ordered = _ear_clip(polygon)
    return triangles, ordered


def visibility_polygon(viewpoint: Point, polygon: list[Point]) -> list[Point]:
    from .polygon_visibility import visibility_polygon as _visibility_polygon

    return _visibility_polygon(viewpoint, polygon)


def polygon_kernel(polygon: list[Point]) -> list[Point]:
    from .polygon_visibility import polygon_kernel as _polygon_kernel

    return _polygon_kernel(polygon)


def shortest_path_in_polygon(
    polygon: list[Point], source: Point, target: Point
) -> tuple[list[Point], float]:
    from .polygon_path import shortest_path_in_polygon as _shortest_path_in_polygon

    return _shortest_path_in_polygon(polygon, source, target)


def triangulate_polygon_with_holes(
    outer_boundary: list[Point],
    holes: list[list[Point]] | None = None,
) -> tuple[list[tuple[Point, Point, Point]], list[Point]]:
    from .polygon_decomposer import _triangulate_with_holes

    return _triangulate_with_holes(outer_boundary, holes)


def get_triangulation_with_diagonals(
    polygon: list[Point],
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
    from .polygon_decomposer import _triangulation_with_diagonals

    return _triangulation_with_diagonals(polygon)


def hertel_mehlhorn(polygon_input: list[Point]) -> tuple[list[list[int]], list[Point]]:
    from .polygon_decomposer import _hertel_mehlhorn

    return _hertel_mehlhorn(polygon_input)


def graham_scan(points: list[Point]) -> list[Point]:
    from .convex_hull import graham_scan as _graham_scan

    return _graham_scan(points)


def monotone_chain(points: list[Point]) -> list[Point]:
    from .convex_hull import monotone_chain as _monotone_chain

    return _monotone_chain(points)


def generate_random_convex_polygon(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    from .polygon_factory import generate_random_convex_polygon as _generate_random_convex_polygon

    return _generate_random_convex_polygon(num_points, x_range, y_range)


def is_convex(polygon: list[Point]) -> bool:
    from .polygon_metrics import is_convex as _is_convex

    return _is_convex(polygon)


def generate_simple_polygon(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    from .polygon_factory import generate_simple_polygon as _generate_simple_polygon

    return _generate_simple_polygon(n_points, x_range, y_range)


def get_reflex_vertices(polygon: list[Point]) -> list[Point]:
    from .polygon_metrics import get_reflex_vertices as _get_reflex_vertices

    return _get_reflex_vertices(polygon)


def generate_points_in_triangle(
    a: Union[Point, Point3D],
    b: Union[Point, Point3D],
    c: Union[Point, Point3D],
    n_points: int = 100,
) -> list[Union[Point, Point3D]]:
    """Sample points uniformly from the interior of a triangle (2D or 3D)."""
    is_3d = isinstance(a, Point3D) or isinstance(b, Point3D) or isinstance(c, Point3D)

    samples: list[Union[Point, Point3D]] = []
    for _ in range(n_points):
        r1 = random.random()
        r2 = random.random()
        if r1 + r2 > 1:
            r1, r2 = 1 - r1, 1 - r2

        px = a.x + r1 * (b.x - a.x) + r2 * (c.x - a.x)
        py = a.y + r1 * (b.y - a.y) + r2 * (c.y - a.y)

        if is_3d:
            az = getattr(a, "z", 0.0)
            bz = getattr(b, "z", 0.0)
            cz = getattr(c, "z", 0.0)
            pz = az + r1 * (bz - az) + r2 * (cz - az)
            samples.append(Point3D(px, py, pz))
        else:
            samples.append(Point(px, py))

    return samples


def get_convex_diameter(polygon: List[Point]) -> float:
    from .polygon_metrics import get_convex_diameter as _get_convex_diameter

    return _get_convex_diameter(polygon)


__all__ = [
    "ConvexHull",
    "Polygon",
    "PolygonProperties",
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
    "monotone_chain",
    "polygon_kernel",
    "shortest_path_in_polygon",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
    "visibility_polygon",
]
