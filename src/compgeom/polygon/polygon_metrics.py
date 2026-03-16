"""Polygon metric and shape-query helpers."""

from __future__ import annotations

import math
from typing import Sequence

from ..kernel import Point2D, cross_product, distance
from .polygon import Polygon, PolygonProperties


def get_polygon_properties(polygon: Polygon | Sequence[Point2D]) -> PolygonProperties:
    """Returns the geometric properties of a polygon."""
    if isinstance(polygon, Polygon):
        return polygon.properties()
    return Polygon(polygon).properties()


def is_polygon_convex(polygon: Polygon | Sequence[Point2D]) -> bool:
    """Checks if a polygon is convex."""
    if isinstance(polygon, Polygon):
        return polygon.is_convex()
    return Polygon(polygon).is_convex()


def get_reflex_vertices(polygon: Polygon | Sequence[Point2D]) -> list[Point2D]:
    """Returns the list of reflex vertices in a polygon."""
    if isinstance(polygon, Polygon):
        return polygon.reflex_vertices()
    return Polygon(polygon).reflex_vertices()


def get_convex_diameter(polygon: Polygon | Sequence[Point2D]) -> float:
    """Returns the diameter of a convex polygon."""
    if isinstance(polygon, Polygon):
        return polygon.convex_diameter()
    return Polygon(polygon).convex_diameter()



def is_point_in_polygon(point: Point2D, polygon: Polygon | Sequence[Point2D]) -> bool:
    """Checks if a point is inside a polygon."""
    if isinstance(polygon, Polygon):
        return polygon.contains_point(point)
    return Polygon(polygon).contains_point(point)

__all__ = ["get_polygon_properties", "is_point_in_polygon", "is_polygon_convex", "get_reflex_vertices", "get_convex_diameter"]
