"""Core polygon data structures."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Sequence, TypeVar, Tuple, Union

from compgeom.kernel import (
    Point2D,
    Point3D,
    is_on_segment,
    cross_product,
    signed_area_twice,
    distance,
)
from compgeom.mesh.surface.polygon import PolygonMesh
from compgeom.polygon.tolerance import EPSILON, is_zero, are_close, is_negative


def triangulate_polygon_with_holes(*args, **kwargs):
    from compgeom.polygon.decomposer import triangulate_polygon_with_holes as func

    return func(*args, **kwargs)


def get_convex_diameter(*args, **kwargs):
    from compgeom.polygon.polygon_metrics import get_convex_diameter as func

    return func(*args, **kwargs)


PolygonT = TypeVar("PolygonT", bound="Polygon")


@dataclass(frozen=True, slots=True)
class PolygonProperties:
    area: float
    centroid: Point2D
    orientation: str

    def __iter__(self):
        yield self.area
        yield self.centroid
        yield self.orientation


@dataclass(frozen=True, slots=True)
class Polygon:
    vertices: tuple[Point2D, ...]

    def __init__(self, vertices: Sequence[Point2D]):
        object.__setattr__(self, "vertices", tuple(vertices))

    def __iter__(self):
        return iter(self.vertices)

    def __len__(self) -> int:
        return len(self.vertices)

    def __getitem__(self, index: int) -> Point2D:
        return self.vertices[index]

    @property
    def area(self) -> float:
        """Calculate polygon area using the shoelace formula."""
        area = 0.0
        n = len(self.vertices)
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            area += (p1.x * p2.y) - (p2.x * p1.y)
        return abs(area) / 2.0

    def as_list(self) -> list[Point2D]:
        return list(self.vertices)

    def ensure_ccw(self) -> Polygon:
        if signed_area_twice(self.as_list()) >= 0:
            return self
        return Polygon(list(reversed(self.vertices)))

    def ensure_cw(self) -> Polygon:
        if signed_area_twice(self.as_list()) <= 0:
            return self
        return Polygon(list(reversed(self.vertices)))

    def properties(self) -> PolygonProperties:
        n = len(self.vertices)
        if n < 3:
            return PolygonProperties(0.0, Point2D(0, 0), "Degenerate")

        area_twice = 0.0
        centroid_x = 0.0
        centroid_y = 0.0
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            cross = (p1.x * p2.y) - (p2.x * p1.y)
            area_twice += cross
            centroid_x += (p1.x + p2.x) * cross
            centroid_y += (p1.y + p2.y) * cross

        area = area_twice / 2.0
        if is_zero(area, tol=1e-12):
            return PolygonProperties(0.0, Point2D(0, 0), "Degenerate")

        centroid_x /= 6.0 * area
        centroid_y /= 6.0 * area
        orientation = "CCW" if area > 0 else "CW"
        return PolygonProperties(abs(area), Point2D(centroid_x, centroid_y), orientation)

    def rotate(self, angle: float, center: Point2D | None = None) -> Polygon:
        """Rotate a polygon by a given angle (in radians) around a center point."""
        if not self.vertices:
            return self

        if center is None:
            center = self.properties().centroid

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        new_vertices = [
            Point2D(
                (p.x - center.x) * cos_a - (p.y - center.y) * sin_a + center.x,
                (p.x - center.x) * sin_a + (p.y - center.y) * cos_a + center.y,
            )
            for p in self.vertices
        ]
        return Polygon(new_vertices)

    def contains_point(self, point: Point2D) -> bool:
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

    def point_on_boundary(self, point: Point2D) -> bool:
        n = len(self.vertices)
        if n == 0:
            return False
        for i in range(n):
            if is_on_segment(point, self.vertices[i], self.vertices[(i + 1) % n]):
                return True
        return False

    def cleanup(self) -> Polygon:
        if not self.vertices:
            return self

        cleaned: list[Point2D] = []
        for point in self.vertices:
            if cleaned and are_close(point, cleaned[-1], tol=1e-7):
                continue
            cleaned.append(point)

        if len(cleaned) > 1 and are_close(cleaned[0], cleaned[-1], tol=1e-7):
            cleaned.pop()

        simplified: list[Point2D] = []
        for point in cleaned:
            if len(simplified) < 2:
                simplified.append(point)
                continue
            if is_zero(cross_product(simplified[-2], simplified[-1], point), tol=1e-7) and is_on_segment(
                simplified[-1], simplified[-2], point
            ):
                simplified[-1] = point
                continue
            simplified.append(point)

        if len(simplified) >= 3 and is_zero(cross_product(simplified[-2], simplified[-1], simplified[0]), tol=1e-7):
            if is_on_segment(simplified[-1], simplified[-2], simplified[0]):
                simplified.pop()
        return Polygon(simplified)

    def is_convex(self) -> bool:
        if len(self.vertices) < 3:
            return True

        turn_directions = [
            cross_product(
                self.vertices[i],
                self.vertices[(i + 1) % len(self.vertices)],
                self.vertices[(i + 2) % len(self.vertices)],
            )
            for i in range(len(self.vertices))
        ]
        non_zero_turns = [turn > 0 for turn in turn_directions if not is_zero(turn, tol=EPSILON)]
        return all(non_zero_turns) or not any(non_zero_turns)

    def reflex_vertices(self) -> list[Point2D]:
        if len(self.vertices) < 3:
            return []

        poly = self.ensure_ccw().as_list()
        reflex = []
        for i in range(len(poly)):
            p_prev = poly[i - 1]
            p_curr = poly[i]
            p_next = poly[(i + 1) % len(poly)]
            if is_negative(cross_product(p_prev, p_curr, p_next), tol=EPSILON):
                reflex.append(p_curr)
        return reflex

    def convex_diameter(self) -> float:
        if len(self.vertices) < 2:
            return 0.0
        if len(self.vertices) == 2:
            return distance(self.vertices[0], self.vertices[1])

        n = len(self.vertices)
        max_d_sq = 0.0
        k = 1

        for i in range(n):
            while True:
                area = abs(cross_product(self.vertices[i], self.vertices[(i + 1) % n], self.vertices[k]))
                next_area = abs(cross_product(self.vertices[i], self.vertices[(i + 1) % n], self.vertices[(k + 1) % n]))
                if next_area > area:
                    k = (k + 1) % n
                else:
                    break

            d1 = (self.vertices[i].x - self.vertices[k].x) ** 2 + (self.vertices[i].y - self.vertices[k].y) ** 2
            d2 = (self.vertices[(i + 1) % n].x - self.vertices[k].x) ** 2 + (
                self.vertices[(i + 1) % n].y - self.vertices[k].y
            ) ** 2
            max_d_sq = max(max_d_sq, d1, d2)

        return math.sqrt(max_d_sq)


@dataclass(frozen=True, slots=True)
class Triangle:
    a: Union[Point2D, Point3D]
    b: Union[Point2D, Point3D]
    c: Union[Point2D, Point3D]

    def sample_points(self, n_points: int = 100) -> list[Union[Point2D, Point3D]]:
        is_3d = isinstance(self.a, Point3D) or isinstance(self.b, Point3D) or isinstance(self.c, Point3D)

        samples: list[Union[Point2D, Point3D]] = []
        for _ in range(n_points):
            r1 = random.random()
            r2 = random.random()
            if r1 + r2 > 1:
                r1, r2 = 1 - r1, 1 - r2

            px = self.a.x + r1 * (self.b.x - self.a.x) + r2 * (self.c.x - self.a.x)
            py = self.a.y + r1 * (self.b.y - self.a.y) + r2 * (self.c.y - self.a.y)

            if is_3d:
                az = getattr(self.a, "z", 0.0)
                bz = getattr(self.b, "z", 0.0)
                cz = getattr(self.c, "z", 0.0)
                pz = az + r1 * (bz - az) + r2 * (cz - az)
                samples.append(Point3D(px, py, pz))
            else:
                samples.append(Point2D(px, py))

        return samples


__all__ = [
    "Polygon",
    "PolygonProperties",
    "Triangle",
    "generate_points_in_triangle",
]


def generate_points_in_triangle(
    a: Point2D | Point3D, b: Point2D | Point3D, c: Point2D | Point3D, n_points: int = 100
) -> list[Point2D | Point3D]:
    """Generates random points within a triangle."""
    return Triangle(a, b, c).sample_points(n_points)
