"""Low-level geometry primitives and predicates."""

from __future__ import annotations

from decimal import Decimal, getcontext
from dataclasses import dataclass
from typing import Optional

EPSILON = 1e-9


def _decimal_orientation(a: Point, b: Point, c: Point) -> Decimal:
    getcontext().prec = 50
    ax = Decimal(str(a.x))
    ay = Decimal(str(a.y))
    bx = Decimal(str(b.x))
    by = Decimal(str(b.y))
    cx = Decimal(str(c.x))
    cy = Decimal(str(c.y))
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def _decimal_incircle(a: Point, b: Point, c: Point, d: Point) -> Decimal:
    getcontext().prec = 50
    adx_d = Decimal(str(a.x)) - Decimal(str(d.x))
    ady_d = Decimal(str(a.y)) - Decimal(str(d.y))
    bdx_d = Decimal(str(b.x)) - Decimal(str(d.x))
    bdy_d = Decimal(str(b.y)) - Decimal(str(d.y))
    cdx_d = Decimal(str(c.x)) - Decimal(str(d.x))
    cdy_d = Decimal(str(c.y)) - Decimal(str(d.y))
    return (
        (adx_d * adx_d + ady_d * ady_d) * (bdx_d * cdy_d - cdx_d * bdy_d)
        - (bdx_d * bdx_d + bdy_d * bdy_d) * (adx_d * cdy_d - cdx_d * ady_d)
        + (cdx_d * cdx_d + cdy_d * cdy_d) * (adx_d * bdy_d - bdx_d * ady_d)
    )


@dataclass(frozen=True, eq=False)
class Point:
    x: float
    y: float
    id: int = -1

    def __repr__(self) -> str:
        return f"P{self.id}({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Point)
            and abs(self.x - other.x) < EPSILON
            and abs(self.y - other.y) < EPSILON
        )

    def __hash__(self) -> int:
        return hash((round(self.x / EPSILON), round(self.y / EPSILON)))


def cross_product(origin: Point, a: Point, b: Point) -> float:
    """Return the signed area of OA x OB."""
    return (a.x - origin.x) * (b.y - origin.y) - (a.y - origin.y) * (b.x - origin.x)


def orientation(a: Point, b: Point, c: Point) -> float:
    """Return the signed orientation determinant of the triangle ABC."""
    value = cross_product(a, b, c)
    if abs(value) > EPSILON:
        return value
    return float(_decimal_orientation(a, b, c))


def orientation_sign(a: Point, b: Point, c: Point) -> int:
    value = orientation(a, b, c)
    if value > EPSILON:
        return 1
    if value < -EPSILON:
        return -1
    exact = _decimal_orientation(a, b, c)
    if exact > 0:
        return 1
    if exact < 0:
        return -1
    return 0


def dot_product(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def sub(a: Point, b: Point) -> Point:
    return Point(a.x - b.x, a.y - b.y)


def length_sq(point: Point) -> float:
    return point.x**2 + point.y**2


def length(point: Point) -> float:
    return length_sq(point) ** 0.5


def get_circumcenter(a: Point, b: Point, c: Point) -> Optional[Point]:
    denominator = 2 * (
        a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)
    )
    if abs(denominator) < 1e-12:
        return None

    ux = (
        (a.x**2 + a.y**2) * (b.y - c.y)
        + (b.x**2 + b.y**2) * (c.y - a.y)
        + (c.x**2 + c.y**2) * (a.y - b.y)
    ) / denominator
    uy = (
        (a.x**2 + a.y**2) * (c.x - b.x)
        + (b.x**2 + b.y**2) * (a.x - c.x)
        + (c.x**2 + c.y**2) * (b.x - a.x)
    ) / denominator
    return Point(ux, uy)


def intersect_lines(p1: Point, p2: Point, p3: Point, p4: Point) -> Optional[Point]:
    """Return the line-line intersection, or ``None`` for parallel lines."""
    denominator = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
    if abs(denominator) < 1e-12:
        return None

    px = (
        (p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x)
        - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)
    ) / denominator
    py = (
        (p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y)
        - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)
    ) / denominator
    return Point(px, py)


def clip_polygon(polygon: list[Point], line_start: Point, line_end: Point) -> list[Point]:
    """Clip a polygon against the left half-plane of the directed line."""

    def is_inside(point: Point) -> bool:
        return cross_product(line_start, line_end, point) >= -1e-12

    clipped: list[Point] = []
    for index, current in enumerate(polygon):
        nxt = polygon[(index + 1) % len(polygon)]
        current_inside = is_inside(current)
        next_inside = is_inside(nxt)

        if current_inside and next_inside:
            clipped.append(nxt)
        elif current_inside and not next_inside:
            intersection = intersect_lines(current, nxt, line_start, line_end)
            if intersection is not None:
                clipped.append(intersection)
        elif not current_inside and next_inside:
            intersection = intersect_lines(current, nxt, line_start, line_end)
            if intersection is not None:
                clipped.append(intersection)
            clipped.append(nxt)
    return clipped


def dist_point_to_segment(point: Point, start: Point, end: Point) -> float:
    """Return the minimum distance from a point to a line segment."""
    segment = sub(end, start)
    from_start = sub(point, start)
    from_end = sub(point, end)

    segment_length_sq = length_sq(segment)
    projection = dot_product(from_start, segment) / segment_length_sq if segment_length_sq > 0 else 0
    if projection < 0:
        return length(from_start)
    if projection > 1:
        return length(from_end)

    closest = Point(start.x + projection * segment.x, start.y + projection * segment.y)
    return length(sub(point, closest))


def is_on_segment(point: Point, start: Point, end: Point) -> bool:
    if abs(cross_product(start, end, point)) > EPSILON:
        return False
    return (
        min(start.x, end.x) - EPSILON <= point.x <= max(start.x, end.x) + EPSILON
        and min(start.y, end.y) - EPSILON <= point.y <= max(start.y, end.y) + EPSILON
    )


def contains_point(triangle, point: Point) -> bool:
    a, b, c = triangle.vertices
    cp1 = orientation(a, b, point)
    cp2 = orientation(b, c, point)
    cp3 = orientation(c, a, point)
    return (
        cp1 >= -EPSILON and cp2 >= -EPSILON and cp3 >= -EPSILON
    ) or (
        cp1 <= EPSILON and cp2 <= EPSILON and cp3 <= EPSILON
    )


def incircle_det(a: Point, b: Point, c: Point, d: Point) -> float:
    adx, ady = a.x - d.x, a.y - d.y
    bdx, bdy = b.x - d.x, b.y - d.y
    cdx, cdy = c.x - d.x, c.y - d.y

    determinant = (
        (adx * adx + ady * ady) * (bdx * cdy - cdx * bdy)
        - (bdx * bdx + bdy * bdy) * (adx * cdy - cdx * ady)
        + (cdx * cdx + cdy * cdy) * (adx * bdy - bdx * ady)
    )
    if abs(determinant) > EPSILON:
        return determinant
    return float(_decimal_incircle(a, b, c, d))


def incircle_sign(a: Point, b: Point, c: Point, d: Point) -> int:
    determinant = incircle_det(a, b, c, d)
    orient = orientation_sign(a, b, c)
    adjusted = determinant * orient
    if adjusted > EPSILON:
        return 1
    if adjusted < -EPSILON:
        return -1
    exact = _decimal_incircle(a, b, c, d)
    if orient < 0:
        exact = -exact
    if exact > 0:
        return 1
    if exact < 0:
        return -1
    return 0


def in_circle(a: Point, b: Point, c: Point, d: Point) -> bool:
    return incircle_sign(a, b, c, d) > 0


__all__ = [
    "EPSILON",
    "Point",
    "clip_polygon",
    "contains_point",
    "cross_product",
    "dist_point_to_segment",
    "dot_product",
    "get_circumcenter",
    "incircle_det",
    "incircle_sign",
    "in_circle",
    "intersect_lines",
    "is_on_segment",
    "length",
    "length_sq",
    "orientation",
    "orientation_sign",
    "sub",
]
