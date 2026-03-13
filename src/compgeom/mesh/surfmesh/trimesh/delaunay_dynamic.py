"""Dynamic Delaunay Triangulation for incremental point insertion."""

from __future__ import annotations
from ....kernel import EPSILON, Point2D, cross_product, in_circle


class DTriangle:
    """A triangle for dynamic Delaunay triangulation with neighbor management."""
    def __init__(self, v1: Point2D, v2: Point2D, v3: Point2D):
        self.v = [v1, v2, v3] if cross_product(v1, v2, v3) >= 0 else [v1, v3, v2]
        self.n: list[DTriangle | None] = [None, None, None]

    def set_neighbor(self, vertex_index: int, neighbor: DTriangle | None):
        self.n[vertex_index] = neighbor
        if neighbor is None:
            return
        for index in range(3):
            v1 = self.v[(vertex_index + 1) % 3]
            v2 = self.v[(vertex_index + 2) % 3]
            if neighbor.v[(index + 1) % 3] == v2 and neighbor.v[(index + 2) % 3] == v1:
                neighbor.n[index] = self
                break

    def has_vertex(self, point: Point2D) -> bool:
        return point in self.v

    def contains_point(self, point: Point2D) -> bool:
        return all(
            cross_product(self.v[index], self.v[(index + 1) % 3], point) >= -EPSILON
            for index in range(3)
        )


class DynamicDelaunay:
    """A class for managing incremental Delaunay triangulation."""
    def __init__(self, width: float = 1000, height: float = 1000):
        s1 = Point2D(width / 2, height * 10, id=-1)
        s2 = Point2D(-width * 10, -height * 10, id=-2)
        s3 = Point2D(width * 10, -height * 10, id=-3)
        self.super_vertices = [s1, s2, s3]
        self.triangles = {DTriangle(s1, s2, s3)}
        self.points: list[Point2D] = []

    def find_containing_triangle(self, point: Point2D) -> DTriangle | None:
        if not self.triangles:
            return None
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

    def add_point(self, point: Point2D):
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
                    old_neighbor.n[neighbor_index] = [t1, t2, t0][index]
                    break

        self.triangles.remove(triangle)
        self.triangles.update([t0, t1, t2])
        self.points.append(point)
        self.legalize_edge(point, t0, 0)
        self.legalize_edge(point, t1, 0)
        self.legalize_edge(point, t2, 0)

    def legalize_edge(self, point: Point2D, triangle: DTriangle, index: int):
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
                if n_ac.v[(probe + 1) % 3] == a and n_ac.v[(probe + 2) % 3] == c:
                    n_ac.n[probe] = neighbor

        self.legalize_edge(point, triangle, 0)
        self.legalize_edge(point, neighbor, 0)

    def get_triangles(self) -> list[tuple[Point2D, Point2D, Point2D]]:
        return [
            tuple(triangle.v)
            for triangle in self.triangles
            if not any(vertex in self.super_vertices for vertex in triangle.v)
        ]
