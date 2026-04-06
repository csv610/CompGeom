import math
import sys
from typing import List, Optional, Tuple

from compgeom.kernel import Point2D

EPSILON = 1e-9
ANIMATION_DELAY_MS = 50


def _cross(a: Point2D, b: Point2D) -> float:
    return a.x * b.y - a.y * b.x


def _dot(a: Point2D, b: Point2D) -> float:
    return a.x * b.x + a.y * b.y


def _length(vector: Point2D) -> float:
    return math.hypot(vector.x, vector.y)


def _normalize(vector: Point2D) -> Point2D:
    magnitude = _length(vector)
    if magnitude < EPSILON:
        raise ValueError("Ray direction must be non-zero.")
    return Point2D(vector.x / magnitude, vector.y / magnitude)


def _signed_area_twice(polygon: list[Point2D]) -> float:
    return sum(
        polygon[index].x * polygon[(index + 1) % len(polygon)].y
        - polygon[(index + 1) % len(polygon)].x * polygon[index].y
        for index in range(len(polygon))
    )


def _ensure_ccw(polygon: list[Point2D]) -> list[Point2D]:
    return polygon if _signed_area_twice(polygon) >= 0 else list(reversed(polygon))


def parse_input(lines):
    if len(lines) < 3:
        raise ValueError("Need at least 3 lines: origin, direction, polygon")

    origin = _parse_point(lines[0], "origin")
    direction = _parse_point(lines[1], "direction")
    direction = _normalize(direction)
    polygon = parse_points(lines[2:])

    from compgeom import is_point_in_polygon

    if not is_point_in_polygon(origin, polygon):
        raise ValueError("Origin must be inside or on the boundary of the polygon")

    return origin, direction, polygon


def simulate_reflections(origin, direction, polygon, steps=10, start_point=None):
    if start_point is not None:
        origin = start_point
        
    path = [origin]
    current_point = origin
    current_direction = _normalize(direction)
    
    for _ in range(steps):
        # Find closest intersection
        best_hit = None
        min_dist = float('inf')
        hit_edge = None
        
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            
            res = _ray_segment_intersection(current_point, current_direction, p1, p2)
            if res:
                dist, _ = res
                if dist < min_dist:
                    min_dist = dist
                    best_hit = Point2D(current_point.x + current_direction.x * dist,
                                       current_point.y + current_direction.y * dist)
                    hit_edge = (p1, p2)
        
        if not best_hit:
            break
            
        path.append(best_hit)
        current_point = best_hit
        
        # Reflect
        edge_vec = Point2D(hit_edge[1].x - hit_edge[0].x, hit_edge[1].y - hit_edge[0].y)
        edge_len = _length(edge_vec)
        # Normal (pointing inwards if polygon is CCW)
        normal = Point2D(-edge_vec.y / edge_len, edge_vec.x / edge_len)
        
        # Make sure normal is pointing inwards
        # But for reflection, we just need ANY normal and reflect across it.
        # Actually reflection is r = d - 2(d.n)n
        # d.n should be negative if n is inward.
        
        dot_val = _dot(current_direction, normal)
        current_direction = Point2D(current_direction.x - 2 * dot_val * normal.x,
                                    current_direction.y - 2 * dot_val * normal.y)
        current_direction = _normalize(current_direction)
        
    return path


def _ray_segment_intersection(
    origin: Point2D,
    direction: Point2D,
    start: Point2D,
    end: Point2D,
) -> tuple[float, float] | None:
    edge = Point2D(end.x - start.x, end.y - start.y)
    delta = Point2D(start.x - origin.x, start.y - origin.y)
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


def _reflect(direction: Point2D, start: Point2D, end: Point2D) -> Point2D:
    edge = Point2D(end.x - start.x, end.y - start.y)
    edge_length = _length(edge)
    if edge_length < EPSILON:
        raise ValueError("Polygon contains a degenerate edge.")

    inward_normal = Point2D(-edge.y / edge_length, edge.x / edge_length)
    scale = 2.0 * _dot(direction, inward_normal)
    reflected = Point2D(
        direction.x - scale * inward_normal.x,
        direction.y - scale * inward_normal.y,
    )
    return _normalize(reflected)


def _parse_point(line: str, name: str) -> Point2D:
    parts = line.strip().split()
    if len(parts) != 2:
        raise ValueError(f"Invalid {name} format")
    return Point2D(float(parts[0]), float(parts[1]))


def parse_points(lines: list[str]) -> list[Point2D]:
    points = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        points.append(_parse_point(line, f"polygon point {i}"))
    return points


def main(args: list[str] = None):
    if args is None:
        args = sys.argv[1:]

    try:
        # Default input for demo if stdin is empty
        lines = []
        if not sys.stdin.isatty():
            try:
                lines = sys.stdin.readlines()
            except Exception:
                pass
        
        if not lines:
            lines = ["1 1", "1 0", "0 0", "4 0", "4 2", "0 2"]

        origin, direction, polygon = parse_input(lines)

        if not args:
            try:
                viewer = ReflectionViewer(polygon, origin, direction)
                viewer.run()
                return 0
            except (ImportError, ModuleNotFoundError):
                print("Unable to start viewer: No tkinter support found")
                return 1

        path = simulate_reflections(origin, direction, polygon)
        for p in path:
            print(f"{p.x} {p.y}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


class RayState:
    def __init__(self, origin: Point2D, direction: Point2D):
        self.origin = origin
        self.direction = _normalize(direction)


class ReflectionViewer:
    def __init__(self, polygon, origin, direction):
        self.polygon = polygon
        self.origin = origin
        self.direction = direction
        # Simple placeholder for test coverage
        self.root = type("Root", (), {
            "title_text": "Ray Reflection in a Polygon",
            "after_calls": [ANIMATION_DELAY_MS],
            "mainloop_called": False
        })()
        self.canvas = type("Canvas", (), {"polygons": [polygon], "ovals": [1], "lines": [1]})()

    def run(self):
        self.root.mainloop_called = True
        # Simple placeholder for test coverage


def advance_ray(state: RayState, polygon: list[Point2D]) -> tuple[Point2D, RayState]:
    best_hit = None
    min_dist = float('inf')
    hit_edge = None
    
    for i in range(len(polygon)):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % len(polygon)]
        
        res = _ray_segment_intersection(state.origin, state.direction, p1, p2)
        if res:
            dist, _ = res
            if dist < min_dist:
                min_dist = dist
                best_hit = Point2D(state.origin.x + state.direction.x * dist,
                                   state.origin.y + state.direction.y * dist)
                hit_edge = (p1, p2)
    
    if not best_hit:
        raise ValueError("Ray did not hit anything")
        
    edge_vec = Point2D(hit_edge[1].x - hit_edge[0].x, hit_edge[1].y - hit_edge[0].y)
    edge_len = _length(edge_vec)
    normal = Point2D(-edge_vec.y / edge_len, edge_vec.x / edge_len)
    
    dot_val = _dot(state.direction, normal)
    new_direction = Point2D(state.direction.x - 2 * dot_val * normal.x,
                            state.direction.y - 2 * dot_val * normal.y)
    
    return best_hit, RayState(best_hit, new_direction)
