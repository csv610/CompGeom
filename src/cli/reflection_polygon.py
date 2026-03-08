from __future__ import annotations

import math
import sys
from dataclasses import dataclass

from geometry_utils import EPSILON, Point
from polygon_utils import is_point_in_polygon


CANVAS_WIDTH = 900
CANVAS_HEIGHT = 700
CANVAS_MARGIN = 40
ANIMATION_DELAY_MS = 20
SEGMENTS_PER_FRAME = 3


@dataclass(frozen=True)
class RayState:
    origin: Point
    direction: Point


def _cross(a: Point, b: Point) -> float:
    return a.x * b.y - a.y * b.x


def _dot(a: Point, b: Point) -> float:
    return a.x * b.x + a.y * b.y


def _length(vector: Point) -> float:
    return math.hypot(vector.x, vector.y)


def _normalize(vector: Point) -> Point:
    magnitude = _length(vector)
    if magnitude < EPSILON:
        raise ValueError("Ray direction must be non-zero.")
    return Point(vector.x / magnitude, vector.y / magnitude)


def _signed_area_twice(polygon: list[Point]) -> float:
    return sum(
        polygon[index].x * polygon[(index + 1) % len(polygon)].y
        - polygon[(index + 1) % len(polygon)].x * polygon[index].y
        for index in range(len(polygon))
    )


def _ensure_ccw(polygon: list[Point]) -> list[Point]:
    return polygon if _signed_area_twice(polygon) >= 0 else list(reversed(polygon))


def parse_input(lines: list[str]) -> tuple[Point, Point, list[Point]]:
    cleaned = [line.strip() for line in lines if line.strip()]
    if len(cleaned) < 5:
        raise ValueError(
            "Expected at least 5 non-empty lines: origin, direction, and 3 polygon vertices."
        )

    origin = _parse_point(cleaned[0], "origin")
    direction = _parse_point(cleaned[1], "direction")
    polygon = [_parse_point(line, f"vertex {index - 1}") for index, line in enumerate(cleaned[2:], start=2)]
    if len(polygon) < 3:
        raise ValueError("Polygon must contain at least 3 vertices.")

    polygon = _ensure_ccw(polygon)
    if abs(_signed_area_twice(polygon)) < EPSILON:
        raise ValueError("Polygon must have non-zero area.")
    if not is_point_in_polygon(origin, polygon):
        raise ValueError("Ray origin must lie inside or on the boundary of the polygon.")

    return origin, _normalize(direction), polygon


def _parse_point(text: str, label: str) -> Point:
    parts = text.split()
    if len(parts) != 2:
        raise ValueError(f"Invalid {label}: expected 2 numbers, got {len(parts)}.")
    x, y = map(float, parts)
    return Point(x, y)


def _ray_segment_intersection(
    origin: Point,
    direction: Point,
    start: Point,
    end: Point,
) -> tuple[float, float] | None:
    edge = Point(end.x - start.x, end.y - start.y)
    delta = Point(start.x - origin.x, start.y - origin.y)
    denominator = _cross(direction, edge)
    if abs(denominator) < EPSILON:
        return None

    distance = _cross(delta, edge) / denominator
    edge_factor = _cross(delta, direction) / denominator
    if distance <= EPSILON:
        return None
    if edge_factor < -EPSILON or edge_factor > 1 + EPSILON:
        return None
    return distance, min(max(edge_factor, 0.0), 1.0)


def _reflect(direction: Point, start: Point, end: Point) -> Point:
    edge = Point(end.x - start.x, end.y - start.y)
    edge_length = _length(edge)
    if edge_length < EPSILON:
        raise ValueError("Polygon contains a degenerate edge.")

    inward_normal = Point(-edge.y / edge_length, edge.x / edge_length)
    scale = 2.0 * _dot(direction, inward_normal)
    reflected = Point(
        direction.x - scale * inward_normal.x,
        direction.y - scale * inward_normal.y,
    )
    return _normalize(reflected)


def advance_ray(state: RayState, polygon: list[Point]) -> tuple[Point, RayState]:
    best_distance = math.inf
    candidates: list[tuple[int, float, Point]] = []

    for index, start in enumerate(polygon):
        end = polygon[(index + 1) % len(polygon)]
        hit = _ray_segment_intersection(state.origin, state.direction, start, end)
        if hit is None:
            continue

        distance, factor = hit
        intersection = Point(
            state.origin.x + distance * state.direction.x,
            state.origin.y + distance * state.direction.y,
        )

        if distance < best_distance - 1e-7:
            best_distance = distance
            candidates = [(index, factor, intersection)]
        elif abs(distance - best_distance) <= 1e-7:
            candidates.append((index, factor, intersection))

    if not candidates:
        raise ValueError("Ray does not hit the polygon boundary.")

    for edge_index, _, intersection in candidates:
        start = polygon[edge_index]
        end = polygon[(edge_index + 1) % len(polygon)]
        reflected = _reflect(state.direction, start, end)
        probe = Point(
            intersection.x + reflected.x * 1e-6,
            intersection.y + reflected.y * 1e-6,
        )
        if is_point_in_polygon(probe, polygon):
            next_state = RayState(origin=probe, direction=reflected)
            return intersection, next_state

    edge_index, _, intersection = candidates[0]
    start = polygon[edge_index]
    end = polygon[(edge_index + 1) % len(polygon)]
    reflected = _reflect(state.direction, start, end)
    next_state = RayState(
        origin=Point(
            intersection.x + reflected.x * 1e-6,
            intersection.y + reflected.y * 1e-6,
        ),
        direction=reflected,
    )
    return intersection, next_state


def simulate_reflections(
    origin: Point,
    direction: Point,
    polygon: list[Point],
    steps: int,
) -> list[Point]:
    state = RayState(origin=origin, direction=_normalize(direction))
    points = [origin]
    for _ in range(steps):
        intersection, state = advance_ray(state, polygon)
        points.append(intersection)
    return points


class ReflectionViewer:
    def __init__(self, polygon: list[Point], origin: Point, direction: Point):
        import tkinter as tk

        self.polygon = polygon
        self.state = RayState(origin=origin, direction=_normalize(direction))
        self.path = [origin]
        self._tk = tk

        self.root = tk.Tk()
        self.root.title("Ray Reflection in a Polygon")
        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.scale, self.offset_x, self.offset_y = self._compute_transform()
        self._draw_polygon()
        self._draw_origin(origin)
        self._animate()

    def _compute_transform(self) -> tuple[float, float, float]:
        xs = [point.x for point in self.polygon]
        ys = [point.y for point in self.polygon]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 1.0)
        span_y = max(max_y - min_y, 1.0)

        scale_x = (CANVAS_WIDTH - 2 * CANVAS_MARGIN) / span_x
        scale_y = (CANVAS_HEIGHT - 2 * CANVAS_MARGIN) / span_y
        scale = min(scale_x, scale_y)
        offset_x = CANVAS_MARGIN - min_x * scale + (CANVAS_WIDTH - 2 * CANVAS_MARGIN - span_x * scale) / 2
        offset_y = CANVAS_MARGIN - min_y * scale + (CANVAS_HEIGHT - 2 * CANVAS_MARGIN - span_y * scale) / 2
        return scale, offset_x, offset_y

    def _to_canvas(self, point: Point) -> tuple[float, float]:
        x = point.x * self.scale + self.offset_x
        y = CANVAS_HEIGHT - (point.y * self.scale + self.offset_y)
        return x, y

    def _draw_polygon(self) -> None:
        coords = []
        for point in self.polygon:
            coords.extend(self._to_canvas(point))
        self.canvas.create_polygon(
            coords,
            outline="#666666",
            fill="",
            width=2,
        )

    def _draw_origin(self, origin: Point) -> None:
        x, y = self._to_canvas(origin)
        radius = 4
        self.canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            outline="#00ffff",
            fill="#00ffff",
        )

    def _animate(self) -> None:
        try:
            for _ in range(SEGMENTS_PER_FRAME):
                intersection, self.state = advance_ray(self.state, self.polygon)
                self._draw_segment(self.path[-1], intersection)
                self.path.append(intersection)
        except ValueError:
            return

        self.root.after(ANIMATION_DELAY_MS, self._animate)

    def _draw_segment(self, start: Point, end: Point) -> None:
        x1, y1 = self._to_canvas(start)
        x2, y2 = self._to_canvas(end)
        self.canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    try:
        origin, direction, polygon = parse_input(sys.stdin.readlines())
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        print("Input format:")
        print("  line 1: origin_x origin_y")
        print("  line 2: direction_x direction_y")
        print("  line 3+: polygon vertices x y")
        return

    try:
        viewer = ReflectionViewer(polygon, origin, direction)
    except ModuleNotFoundError as exc:
        print(f"Unable to start viewer: {exc}")
        print("This script requires tkinter support in the local Python installation.")
        return

    viewer.run()


if __name__ == "__main__":
    main()
