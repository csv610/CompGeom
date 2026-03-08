"""Triangulation, Delaunay, and Voronoi algorithms."""

from __future__ import annotations

import math
from collections import deque

from .geometry import (
    EPSILON,
    Point,
    clip_polygon,
    contains_point,
    cross_product,
    in_circle,
    sub,
)


class Triangle:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = (v1, v2, v3)
        self.children: list["Triangle"] = []
        self.is_active = True

    def find_leaves_containing(self, point: Point, found_leaves: set["Triangle"]):
        if not contains_point(self, point):
            return
        if not self.children:
            if self.is_active:
                found_leaves.add(self)
            return
        for child in self.children:
            child.find_leaves_containing(point, found_leaves)


def _create_super_triangle(points: list[Point]) -> tuple[Point, Point, Point]:
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)
    delta = max(max_x - min_x, max_y - min_y, 1.0) * 10
    mid_x = (min_x + max_x) / 2
    return (
        Point(mid_x, max_y + delta, id=-1),
        Point(min_x - delta, min_y - delta, id=-2),
        Point(max_x + delta, min_y - delta, id=-3),
    )


def triangulate(points: list[Point]):
    if not points:
        return [], []

    super_triangle = _create_super_triangle(points)
    super_triangle_vertices = set(super_triangle)
    skipped_points = []
    existing_points = set()
    triangles = [super_triangle]

    def make_ccw(a: Point, b: Point, c: Point):
        return (a, b, c) if cross_product(a, b, c) >= 0 else (a, c, b)

    for point in points:
        if point in existing_points or any(point == vertex for vertex in super_triangle_vertices):
            skipped_points.append((point, "Duplicate/Coincident Point"))
            continue

        bad_triangles = [triangle for triangle in triangles if in_circle(*triangle, point)]
        if not bad_triangles:
            containing = [triangle for triangle in triangles if contains_point(Triangle(*triangle), point)]
            if not containing:
                skipped_points.append((point, "Outside super-triangle (Numerical Error)"))
                continue
            bad_triangles = containing

        edge_counts = {}
        directed_edges = {}
        for triangle in bad_triangles:
            a, b, c = triangle
            for edge in ((a, b), (b, c), (c, a)):
                key = frozenset(edge)
                edge_counts[key] = edge_counts.get(key, 0) + 1
                directed_edges[key] = edge

        triangles = [triangle for triangle in triangles if triangle not in bad_triangles]
        for key, count in edge_counts.items():
            if count != 1:
                continue
            a, b = directed_edges[key]
            triangles.append(make_ccw(a, b, point))
        existing_points.add(point)

    final_triangles = [
        triangle for triangle in triangles if not any(vertex in super_triangle_vertices for vertex in triangle)
    ]
    return final_triangles, skipped_points


class MeshTriangle:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = [v1, v2, v3] if cross_product(v1, v2, v3) >= 0 else [v1, v3, v2]
        self.neighbors = [None, None, None]

    def get_edge(self, index: int):
        v1 = self.vertices[(index + 1) % 3]
        v2 = self.vertices[(index + 2) % 3]
        return tuple(sorted((v1.id, v2.id)))

    def find_neighbor_index(self, other: "MeshTriangle") -> int:
        for index, neighbor in enumerate(self.neighbors):
            if neighbor == other:
                return index
        return -1


def build_topology(triangles):
    mesh = [MeshTriangle(*triangle) for triangle in triangles]
    edge_map = {}
    for triangle_index, triangle in enumerate(mesh):
        for edge_index in range(3):
            edge = triangle.get_edge(edge_index)
            if edge not in edge_map:
                edge_map[edge] = (triangle_index, edge_index)
                continue
            other_triangle_index, other_edge_index = edge_map[edge]
            triangle.neighbors[edge_index] = mesh[other_triangle_index]
            mesh[other_triangle_index].neighbors[other_edge_index] = triangle
    return mesh


def delaunay_flip(mesh):
    queue = deque()
    queued_edges = set()

    for triangle in mesh:
        for edge_index, neighbor in enumerate(triangle.neighbors):
            if neighbor is None:
                continue
            edge = triangle.get_edge(edge_index)
            if edge not in queued_edges:
                queue.append((triangle, edge_index))
                queued_edges.add(edge)

    while queue:
        t1, i1 = queue.popleft()
        edge = t1.get_edge(i1)
        queued_edges.discard(edge)

        t2 = t1.neighbors[i1]
        if t2 is None:
            continue

        i2 = t2.find_neighbor_index(t1)
        a = t1.vertices[i1]
        b = t1.vertices[(i1 + 1) % 3]
        c = t1.vertices[(i1 + 2) % 3]
        d = t2.vertices[i2]

        if not in_circle(a, b, c, d):
            continue

        n_ac = t1.neighbors[(i1 + 1) % 3]
        n_ab = t1.neighbors[(i1 + 2) % 3]
        n_db = t2.neighbors[(i2 + 1) % 3]
        n_dc = t2.neighbors[(i2 + 2) % 3]

        t1.vertices = [a, b, d]
        t2.vertices = [a, d, c]
        t1.neighbors[0], t1.neighbors[1], t1.neighbors[2] = n_db, t2, n_ab
        t2.neighbors[0], t2.neighbors[1], t2.neighbors[2] = n_dc, n_ac, t1

        if n_db:
            n_db.neighbors[n_db.find_neighbor_index(t2)] = t1
        if n_ac:
            n_ac.neighbors[n_ac.find_neighbor_index(t1)] = t2

        for triangle, edge_index in [(t1, 0), (t1, 2), (t2, 0), (t2, 1)]:
            if triangle.neighbors[edge_index] is None:
                continue
            candidate = triangle.get_edge(edge_index)
            if candidate not in queued_edges:
                queue.append((triangle, edge_index))
                queued_edges.add(candidate)


class DTriangle:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.v = [v1, v2, v3] if cross_product(v1, v2, v3) >= 0 else [v1, v3, v2]
        self.n = [None, None, None]

    def set_neighbor(self, vertex_index: int, neighbor: "DTriangle | None"):
        self.n[vertex_index] = neighbor
        if neighbor is None:
            return
        for index in range(3):
            v1 = self.v[(vertex_index + 1) % 3]
            v2 = self.v[(vertex_index + 2) % 3]
            if neighbor.v[(index + 1) % 3] == v2 and neighbor.v[(index + 2) % 3] == v1:
                neighbor.n[index] = self
                break

    def has_vertex(self, point: Point) -> bool:
        return point in self.v

    def contains_point(self, point: Point) -> bool:
        return all(
            cross_product(self.v[index], self.v[(index + 1) % 3], point) >= -EPSILON
            for index in range(3)
        )


class DynamicDelaunay:
    def __init__(self, width=1000, height=1000):
        s1 = Point(width / 2, height * 10, id=-1)
        s2 = Point(-width * 10, -height * 10, id=-2)
        s3 = Point(width * 10, -height * 10, id=-3)
        self.super_vertices = [s1, s2, s3]
        self.triangles = {DTriangle(s1, s2, s3)}
        self.points = []

    def find_containing_triangle(self, point: Point):
        current = next(iter(self.triangles))
        visited = set()
        while current:
            visited.add(current)
            for index in range(3):
                if cross_product(current.v[(index + 1) % 3], current.v[(index + 2) % 3], point) > EPSILON:
                    if current.n[index] and current.n[index] not in visited:
                        current = current.n[index]
                        break
            else:
                return current
        return None

    def add_point(self, point: Point):
        triangle = self.find_containing_triangle(point)
        if triangle is None:
            return

        v0, v1, v2 = triangle.v
        n0, n1, n2 = triangle.n
        t0 = DTriangle(point, v1, v2)
        t1 = DTriangle(point, v2, v0)
        t2 = DTriangle(point, v0, v1)

        t0.n[0], t0.n[1], t0.n[2] = n0, t1, t2
        t1.n[0], t1.n[1], t1.n[2] = n1, t2, t0
        t2.n[0], t2.n[1], t2.n[2] = n2, t0, t1

        for index, old_neighbor in enumerate([n0, n1, n2]):
            if old_neighbor is None:
                continue
            for neighbor_index in range(3):
                if old_neighbor.n[neighbor_index] == triangle:
                    old_neighbor.n[neighbor_index] = [t0, t1, t2][index]
                    break

        self.triangles.remove(triangle)
        self.triangles.update([t0, t1, t2])
        self.points.append(point)
        self.legalize_edge(point, t0, 0)
        self.legalize_edge(point, t1, 0)
        self.legalize_edge(point, t2, 0)

    def legalize_edge(self, point: Point, triangle: DTriangle, index: int):
        neighbor = triangle.n[index]
        if neighbor is None:
            return

        neighbor_index = -1
        for probe in range(3):
            if neighbor.n[probe] == triangle:
                neighbor_index = probe
                break

        a, b, c = triangle.v[index], triangle.v[(index + 1) % 3], triangle.v[(index + 2) % 3]
        d = neighbor.v[neighbor_index]
        if not in_circle(a, b, c, d):
            return

        n_ab = triangle.n[(index + 2) % 3]
        n_ac = triangle.n[(index + 1) % 3]
        n_db = neighbor.n[(neighbor_index + 1) % 3]
        n_dc = neighbor.n[(neighbor_index + 2) % 3]

        triangle.v = [point, b, d]
        neighbor.v = [point, d, c]
        triangle.n = [n_db, neighbor, n_ab]
        neighbor.n = [n_dc, n_ac, triangle]

        if n_db:
            for probe in range(3):
                if n_db.v[(probe + 1) % 3] == d and n_db.v[(probe + 2) % 3] == b:
                    n_db.n[probe] = triangle
        if n_ac:
            for probe in range(3):
                if n_ac.v[(probe + 1) % 3] == c and n_ac.v[(probe + 2) % 3] == a:
                    n_ac.n[probe] = neighbor

        self.legalize_edge(point, triangle, 0)
        self.legalize_edge(point, neighbor, 0)

    def get_triangles(self):
        return [
            triangle.v
            for triangle in self.triangles
            if not any(vertex in self.super_vertices for vertex in triangle.v)
        ]


def get_voronoi_cells(points: list[Point], boundary_polygon: list[Point]):
    cells = []
    for point in points:
        cell = list(boundary_polygon)
        for other in points:
            if point == other:
                continue
            midpoint = Point((point.x + other.x) / 2, (point.y + other.y) / 2)
            direction = sub(other, point)
            bisector_end = Point(midpoint.x - direction.y, midpoint.y + direction.x)
            if cross_product(midpoint, bisector_end, point) < 0:
                cell = clip_polygon(cell, bisector_end, midpoint)
            else:
                cell = clip_polygon(cell, midpoint, bisector_end)
        cells.append((point, cell))
    return cells


def get_square_boundary(size=100, center=(50, 50)):
    cx, cy = center
    half_size = size / 2
    return [
        Point(cx - half_size, cy - half_size),
        Point(cx + half_size, cy - half_size),
        Point(cx + half_size, cy + half_size),
        Point(cx - half_size, cy + half_size),
    ]


def get_circle_boundary(radius=50, center=(50, 50), n_segments=64):
    cx, cy = center
    return [
        Point(cx + radius * math.cos(2 * math.pi * index / n_segments), cy + radius * math.sin(2 * math.pi * index / n_segments))
        for index in range(n_segments)
    ]


__all__ = [
    "DTriangle",
    "DynamicDelaunay",
    "MeshTriangle",
    "Triangle",
    "build_topology",
    "delaunay_flip",
    "get_circle_boundary",
    "get_square_boundary",
    "get_voronoi_cells",
    "triangulate",
]
