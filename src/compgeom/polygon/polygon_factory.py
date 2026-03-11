"""Polygon generation and factory helpers."""

from __future__ import annotations

import math
import random
from typing import TypeVar

from ..kernel import Point
from .convex_hull import MonotoneChain
from .polygon import Polygon

PolygonT = TypeVar("PolygonT", bound=Polygon)


def random_convex_points(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    points = [
        Point(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(num_points)
    ]
    return MonotoneChain().generate(points)


def simple_polygon_points(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    points = [
        Point(random.uniform(*x_range), random.uniform(*y_range), index)
        for index in range(n_points)
    ]
    center_x = sum(point.x for point in points) / n_points
    center_y = sum(point.y for point in points) / n_points
    ordered = sorted(points, key=lambda point: math.atan2(point.y - center_y, point.x - center_x))
    return [Point(point.x, point.y, index) for index, point in enumerate(ordered)]


def random_convex_polygon(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
    *,
    polygon_cls: type[PolygonT] = Polygon,
) -> PolygonT:
    return polygon_cls(random_convex_points(num_points, x_range, y_range))


def simple_polygon(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
    *,
    polygon_cls: type[PolygonT] = Polygon,
) -> PolygonT:
    return polygon_cls(simple_polygon_points(n_points, x_range, y_range))


def generate_random_convex_polygon(
    num_points: int = 10,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    return random_convex_polygon(num_points, x_range, y_range).as_list()


def generate_simple_polygon(
    n_points: int = 20,
    x_range: tuple[float, float] = (0, 100),
    y_range: tuple[float, float] = (0, 100),
) -> list[Point]:
    return simple_polygon(n_points, x_range, y_range).as_list()


__all__ = [
    "generate_random_convex_polygon",
    "generate_simple_polygon",
    "random_convex_polygon",
    "random_convex_points",
    "simple_polygon",
    "simple_polygon_points",
]
