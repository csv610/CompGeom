"""Algorithms for decomposing polygons into simpler pieces."""

from __future__ import annotations

from collections import Counter
from typing import List

from ..geo_math.geometry import EPSILON, Point, contains_point, cross_product, is_on_segment
from ..geo_math.math_utils import distance
from ..mesh.mesh import PolygonMesh
from .line_segment import proper_segment_intersection
from .polygon_utils import ensure_ccw, ensure_cw, point_on_boundary, segment_inside_boundaries


class _TriangleView:
    def __init__(self, v1: Point, v2: Point, v3: Point):
        self.vertices = (v1, v2, v3)

def _is_ear(a: Point, b: Point, c: Point, polygon: list[Point]) -> bool:
    if cross_product(a, b, c) <= 0:
        return False

    triangle = _TriangleView(a, b, c)
    for point in polygon:
        if point is not a and point is not b and point is not c:
            if contains_point(triangle, point):
                return False
    return True


def _ear_clip(
    polygon: list[Point],
    *,
    collect_diagonals: bool = False,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
    ordered = ensure_ccw(list(polygon))
    polygon_size = len(ordered)
    working_polygon = list(ordered)
    working_indices = list(range(polygon_size))
    triangles: list[tuple[int, int, int]] = []
    diagonals: list[tuple[int, int]] = []

    while len(working_indices) > 3:
        for offset, current in enumerate(working_indices):
            prev_index = working_indices[offset - 1]
            next_index = working_indices[(offset + 1) % len(working_indices)]
            if not _is_ear(ordered[prev_index], ordered[current], ordered[next_index], working_polygon):
                continue

            triangles.append((prev_index, current, next_index))
            if collect_diagonals and abs(next_index - prev_index) != 1 and {prev_index, next_index} != {
                0,
                polygon_size - 1,
            }:
                diagonals.append(tuple(sorted((prev_index, next_index))))
            working_indices.pop(offset)
            working_polygon.pop(offset)
            break
        else:
            break

    if len(working_indices) == 3:
        triangles.append(tuple(working_indices))

    return triangles, diagonals, ordered


def _triangulate_with_holes(
    outer_boundary: list[Point],
    holes: list[list[Point]] | None = None,
) -> tuple[list[tuple[Point, Point, Point]], list[Point]]:
    holes = holes or []
    from .polygon import Polygon

    merged_polygon = Polygon(outer_boundary).ensure_ccw()
    for hole in holes:
        merged_polygon = Polygon(_splice_hole(merged_polygon.as_list(), ensure_cw(list(hole))))

    triangle_indices, _, merged_vertices = _ear_clip(merged_polygon.as_list())
    triangles = [tuple(merged_vertices[index] for index in triangle) for triangle in triangle_indices]
    return triangles, merged_vertices


def _triangulation_with_diagonals(
    polygon: list[Point],
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
    return _ear_clip(polygon, collect_diagonals=True)


def _hertel_mehlhorn(polygon_input: list[Point]) -> tuple[list[list[int]], list[Point]]:
    triangles, diagonals, polygon = _triangulation_with_diagonals(polygon_input)
    partitions = [list(triangle) for triangle in triangles]
    reflex_vertices = {
        index
        for index in range(len(polygon))
        if cross_product(polygon[index - 1], polygon[index], polygon[(index + 1) % len(polygon)]) <= 0
    }

    for diagonal in diagonals:
        shared_partitions = [
            partition_index
            for partition_index, partition in enumerate(partitions)
            if diagonal[0] in partition and diagonal[1] in partition
        ]
        if len(shared_partitions) != 2:
            continue

        u, v = diagonal
        if u in reflex_vertices or v in reflex_vertices:
            continue

        first, second = shared_partitions
        merged = list(set(partitions[first]) | set(partitions[second]))
        partitions.pop(max(first, second))
        partitions.pop(min(first, second))
        partitions.append(merged)

    return partitions, polygon


def _domain_contains_point(outer: list[Point], holes: list[list[Point]], point: Point) -> bool:
    from .polygon import Polygon

    if not Polygon(outer).contains_point(point):
        return False
    return not any(Polygon(hole).contains_point(point) and not point_on_boundary(point, hole) for hole in holes)


def _segment_inside_domain(
    outer: list[Point],
    holes: list[list[Point]],
    start: Point,
    end: Point,
    allow_hole_endpoint: Point | None = None,
) -> bool:
    return segment_inside_boundaries(
        start,
        end,
        [outer, *holes],
        lambda midpoint: _domain_contains_point(outer, holes, midpoint),
        allow_boundary_endpoint=allow_hole_endpoint,
    )


def _splice_hole(outer: list[Point], hole: list[Point]) -> list[Point]:
    hole_vertex_index = max(range(len(hole)), key=lambda index: (hole[index].x, -hole[index].y))
    hole_vertex = hole[hole_vertex_index]

    candidates = []
    for outer_index, outer_vertex in enumerate(outer):
        if not _segment_inside_domain(outer, [hole], hole_vertex, outer_vertex, allow_hole_endpoint=hole_vertex):
            continue
        candidates.append((distance(hole_vertex, outer_vertex), outer_index))
    if not candidates:
        raise ValueError("Failed to connect hole to outer boundary.")

    _, outer_index = min(candidates)
    outer_vertex = outer[outer_index]

    rotated_hole = hole[hole_vertex_index:] + hole[:hole_vertex_index]
    merged: list[Point] = []
    merged.extend(outer[: outer_index + 1])
    merged.append(hole_vertex)
    merged.extend(rotated_hole[1:])
    merged.append(hole_vertex)
    merged.append(outer_vertex)
    merged.extend(outer[outer_index + 1 :])
    return merged


def _mesh_from_point_faces(point_faces: List[List[Point]] | List[tuple[Point, ...]]) -> PolygonMesh:
    vertices: list[Point] = []
    faces: list[tuple[int, ...]] = []
    vertex_indices: dict[Point, int] = {}

    for face in point_faces:
        indexed_face = []
        for vertex in face:
            if vertex not in vertex_indices:
                vertex_indices[vertex] = len(vertices)
                vertices.append(vertex)
            indexed_face.append(vertex_indices[vertex])
        faces.append(tuple(indexed_face))

    return PolygonMesh(vertices, faces)


def _ordered_face_from_triangles(
    triangles: list[tuple[int, int, int]],
    vertices: list[Point],
) -> tuple[int, ...] | None:
    if not triangles:
        return None

    edge_counts: Counter[tuple[int, int]] = Counter()
    for a, b, c in triangles:
        for u, v in ((a, b), (b, c), (c, a)):
            edge_counts[tuple(sorted((u, v)))] += 1

    boundary_edges = [edge for edge, count in edge_counts.items() if count == 1]
    if len(boundary_edges) < 3:
        return None

    adjacency: dict[int, list[int]] = {}
    for u, v in boundary_edges:
        adjacency.setdefault(u, []).append(v)
        adjacency.setdefault(v, []).append(u)

    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        return None

    start = min(adjacency)
    face = [start]
    previous = None
    current = start
    while True:
        neighbors = adjacency[current]
        next_vertex = neighbors[0] if neighbors[0] != previous else neighbors[1]
        if next_vertex == start:
            break
        face.append(next_vertex)
        previous, current = current, next_vertex
        if len(face) > len(boundary_edges):
            return None

    area_twice = 0.0
    for i, vertex_index in enumerate(face):
        p1 = vertices[vertex_index]
        p2 = vertices[face[(i + 1) % len(face)]]
        area_twice += p1.x * p2.y - p2.x * p1.y
    if area_twice < 0:
        face.reverse()

    return tuple(face)


def _is_y_monotone(face: tuple[int, ...], vertices: list[Point]) -> bool:
    if len(face) <= 3:
        return True

    top = max(range(len(face)), key=lambda i: (vertices[face[i]].y, -vertices[face[i]].x))
    bottom = min(range(len(face)), key=lambda i: (vertices[face[i]].y, vertices[face[i]].x))

    def chain(step: int) -> list[float]:
        index = top
        ys = [vertices[face[index]].y]
        while index != bottom:
            index = (index + step) % len(face)
            ys.append(vertices[face[index]].y)
        return ys

    for ys in (chain(1), chain(-1)):
        for i in range(1, len(ys)):
            if ys[i] > ys[i - 1] + EPSILON:
                return False
    return True


def _share_triangle_edge(left: list[tuple[int, int, int]], right: list[tuple[int, int, int]]) -> bool:
    return any(len(set(a).intersection(b)) == 2 for a in left for b in right)


def _monotone_partitions(
    triangles: list[tuple[int, int, int]],
    vertices: list[Point],
) -> list[tuple[int, ...]]:
    partitions = [{"triangles": [triangle], "face": tuple(triangle)} for triangle in triangles]

    changed = True
    while changed:
        changed = False
        for i in range(len(partitions)):
            for j in range(i + 1, len(partitions)):
                if not _share_triangle_edge(partitions[i]["triangles"], partitions[j]["triangles"]):
                    continue

                merged_triangles = partitions[i]["triangles"] + partitions[j]["triangles"]
                merged_face = _ordered_face_from_triangles(merged_triangles, vertices)
                if merged_face is None or not _is_y_monotone(merged_face, vertices):
                    continue

                partitions[i] = {"triangles": merged_triangles, "face": merged_face}
                partitions.pop(j)
                changed = True
                break
            if changed:
                break

    return [partition["face"] for partition in partitions]


def _point_on_segment_at_x(start: Point, end: Point, x: float) -> Point | None:
    min_x = min(start.x, end.x) - EPSILON
    max_x = max(start.x, end.x) + EPSILON
    if x < min_x or x > max_x:
        return None
    if abs(end.x - start.x) <= EPSILON:
        if abs(start.x - x) > EPSILON:
            return None
        lower, upper = sorted((start, end), key=lambda p: (p.y, p.x))
        return Point(x, lower.y if lower.y == upper.y else lower.y)

    t = (x - start.x) / (end.x - start.x)
    y = start.y + t * (end.y - start.y)
    return Point(x, y)


def _vertical_line_intersections(polygon: list[Point], x: float) -> list[tuple[float, int]]:
    hits: list[tuple[float, int]] = []
    n = len(polygon)
    for i in range(n):
        start = polygon[i]
        end = polygon[(i + 1) % n]
        if abs(start.x - end.x) <= EPSILON:
            continue
        min_x = min(start.x, end.x)
        max_x = max(start.x, end.x)
        if x < min_x - EPSILON or x >= max_x - EPSILON:
            continue
        point = _point_on_segment_at_x(start, end, x)
        if point is not None:
            hits.append((point.y, i))
    hits.sort(key=lambda item: item[0])
    return hits


def _cleanup_face(points: list[Point]) -> list[Point]:
    face: list[Point] = []
    for point in points:
        if face and point == face[-1]:
            continue
        face.append(point)
    if len(face) > 1 and face[0] == face[-1]:
        face.pop()
    return face


def _trapezoidal_faces(polygon: list[Point]) -> list[list[Point]]:
    x_values = sorted({point.x for point in polygon})
    if len(x_values) < 2:
        return [polygon]

    faces: list[list[Point]] = []
    for left_x, right_x in zip(x_values, x_values[1:]):
        if right_x - left_x <= EPSILON:
            continue
        mid_x = (left_x + right_x) / 2.0
        intersections = _vertical_line_intersections(polygon, mid_x)
        for lower_hit, upper_hit in zip(intersections[0::2], intersections[1::2]):
            _, lower_edge_index = lower_hit
            _, upper_edge_index = upper_hit
            lower_start = polygon[lower_edge_index]
            lower_end = polygon[(lower_edge_index + 1) % len(polygon)]
            upper_start = polygon[upper_edge_index]
            upper_end = polygon[(upper_edge_index + 1) % len(polygon)]

            lower_left = _point_on_segment_at_x(lower_start, lower_end, left_x)
            lower_right = _point_on_segment_at_x(lower_start, lower_end, right_x)
            upper_left = _point_on_segment_at_x(upper_start, upper_end, left_x)
            upper_right = _point_on_segment_at_x(upper_start, upper_end, right_x)
            if None in (lower_left, lower_right, upper_left, upper_right):
                continue

            face = _cleanup_face([lower_left, lower_right, upper_right, upper_left])
            if len(face) >= 3:
                faces.append(face)

    return faces or [polygon]


def _diagonal_crosses(diagonal: tuple[int, int], diagonals: list[tuple[int, int]], polygon: list[Point]) -> bool:
    a, b = diagonal
    for c, d in diagonals:
        if {a, b}.intersection({c, d}):
            continue
        if proper_segment_intersection(polygon[a], polygon[b], polygon[c], polygon[d]):
            return True
    return False


def _split_face_by_diagonal(face: tuple[int, ...], diagonal: tuple[int, int]) -> list[tuple[int, ...]] | None:
    a, b = diagonal
    if a not in face or b not in face:
        return None
    ia = face.index(a)
    ib = face.index(b)
    if (ia - ib) % len(face) in (1, len(face) - 1):
        return None

    if ia > ib:
        ia, ib = ib, ia
        a, b = b, a

    first = face[ia: ib + 1]
    second = face[ib:] + face[: ia + 1]
    if len(first) < 3 or len(second) < 3:
        return None
    return [tuple(first), tuple(second)]


def _visibility_faces(polygon: list[Point]) -> list[tuple[int, ...]]:
    from .polygon import Polygon

    ordered = Polygon(polygon).ensure_ccw().as_list()
    poly = Polygon(ordered)
    n = len(ordered)
    reflex_indices = [
        i
        for i in range(n)
        if ((ordered[i].x - ordered[i - 1].x) * (ordered[(i + 1) % n].y - ordered[i].y))
        - ((ordered[i].y - ordered[i - 1].y) * (ordered[(i + 1) % n].x - ordered[i].x))
        < -EPSILON
    ]

    chosen: list[tuple[int, int]] = []
    for reflex in reflex_indices:
        candidates: list[tuple[float, tuple[int, int]]] = []
        for target in range(n):
            if target == reflex:
                continue
            if target in {(reflex - 1) % n, (reflex + 1) % n}:
                continue
            if not poly._segment_inside(ordered[reflex], ordered[target]):
                continue
            diagonal = tuple(sorted((reflex, target)))
            if diagonal in chosen or _diagonal_crosses(diagonal, chosen, ordered):
                continue
            dx = ordered[reflex].x - ordered[target].x
            dy = ordered[reflex].y - ordered[target].y
            candidates.append((dx * dx + dy * dy, diagonal))
        if candidates:
            _, diagonal = min(candidates, key=lambda item: item[0])
            chosen.append(diagonal)

    faces = [tuple(range(n))]
    for diagonal in chosen:
        updated_faces: list[tuple[int, ...]] = []
        split_done = False
        for face in faces:
            split = _split_face_by_diagonal(face, diagonal)
            if split is None or split_done:
                updated_faces.append(face)
                continue
            updated_faces.extend(split)
            split_done = True
        faces = updated_faces
    return faces


class PolygonDecomposer:
    """Provides polygon decomposition helpers over the core ``Polygon`` API."""

    @staticmethod
    def supported_decompositions() -> list[str]:
        """Returns the public decomposition algorithms supported by this class."""
        return [
            "triangulate",
            "triangulate_with_holes",
            "convex_decomposition",
            "monotone_decomposition",
            "trapezoidal_decomposition",
            "visibility_decomposition",
        ]

    @staticmethod
    def triangulate(polygon: List[Point]) -> PolygonMesh:
        """Triangulates a simple polygon and returns the result as a polygon mesh."""
        triangle_indices, _, vertices = _ear_clip(polygon)
        return PolygonMesh(vertices, triangle_indices)

    @staticmethod
    def triangulate_indices(
        polygon: List[Point],
    ) -> tuple[list[tuple[int, int, int]], list[Point]]:
        """Triangulates a simple polygon and returns triangle indices plus ordered vertices."""
        triangle_indices, _, vertices = _ear_clip(polygon)
        return triangle_indices, vertices

    @staticmethod
    def triangulation_with_diagonals(
        polygon: List[Point],
    ) -> tuple[PolygonMesh, list[tuple[int, int]]]:
        """Triangulates a polygon and returns the mesh plus inserted diagonals."""
        triangle_indices, diagonals, vertices = _triangulation_with_diagonals(polygon)
        return PolygonMesh(vertices, triangle_indices), diagonals

    @staticmethod
    def triangulation_with_diagonals_indices(
        polygon: List[Point],
    ) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
        """Triangulates a polygon and returns triangle indices, diagonals, and ordered vertices."""
        return _triangulation_with_diagonals(polygon)

    @staticmethod
    def triangulate_with_holes(
        outer_boundary: List[Point],
        holes: List[List[Point]] | None = None,
    ) -> PolygonMesh:
        """Triangulates a polygonal domain with holes and returns a polygon mesh."""
        triangles, _ = _triangulate_with_holes(outer_boundary, holes)
        return _mesh_from_point_faces(list(triangles))

    @staticmethod
    def convex_decomposition_indices(polygon: List[Point]) -> tuple[list[list[int]], list[Point]]:
        """Returns convex decomposition partitions as vertex-index lists plus ordered vertices."""
        return _hertel_mehlhorn(polygon)

    @staticmethod
    def hertel_mehlhorn_indices(polygon: List[Point]) -> tuple[list[list[int]], list[Point]]:
        """Returns Hertel-Mehlhorn convex partitions and the ordered polygon vertices."""
        return _hertel_mehlhorn(polygon)

    @staticmethod
    def convex_decomposition(polygon: List[Point]) -> PolygonMesh:
        """Decomposes a simple polygon into convex parts."""
        if len(polygon) < 3:
            return PolygonMesh(list(polygon), [])

        partitions, vertices = PolygonDecomposer.convex_decomposition_indices(polygon)
        faces = [tuple(sorted(partition)) for partition in partitions]
        return PolygonMesh(vertices, faces)

    @staticmethod
    def monotone_decomposition(polygon: List[Point]) -> PolygonMesh:
        """Decomposes a simple polygon into y-monotone parts."""
        if len(polygon) < 3:
            return PolygonMesh(list(polygon), [])

        triangles, _, vertices = _ear_clip(polygon)
        return PolygonMesh(vertices, _monotone_partitions(triangles, vertices))

    @staticmethod
    def trapezoidal_decomposition(polygon: List[Point]) -> PolygonMesh:
        """Decomposes a simple polygon into vertical trapezoidal cells."""
        if len(polygon) < 3:
            return PolygonMesh(list(polygon), [])
        from .polygon import Polygon

        return _mesh_from_point_faces(_trapezoidal_faces(Polygon(polygon).ensure_ccw().as_list()))

    @staticmethod
    def visibility_decomposition(polygon: List[Point]) -> PolygonMesh:
        """Decomposes a simple polygon using non-crossing reflex-visibility diagonals."""
        if len(polygon) < 3:
            return PolygonMesh(list(polygon), [])
        from .polygon import Polygon

        ordered = Polygon(polygon).ensure_ccw().as_list()
        return PolygonMesh(ordered, _visibility_faces(ordered))

def triangulate_polygon(polygon: list[Point]) -> tuple[list[tuple[int, int, int]], list[Point]]:
    return PolygonDecomposer.triangulate_indices(polygon)


def triangulate_polygon_with_holes(
    outer_boundary: list[Point],
    holes: list[list[Point]] | None = None,
) -> tuple[list[tuple[Point, Point, Point]], list[Point]]:
    return _triangulate_with_holes(outer_boundary, holes)


def get_triangulation_with_diagonals(
    polygon: list[Point],
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point]]:
    return PolygonDecomposer.triangulation_with_diagonals_indices(polygon)


def hertel_mehlhorn(polygon: list[Point]) -> tuple[list[list[int]], list[Point]]:
    return _hertel_mehlhorn(polygon)


__all__ = [
    "PolygonDecomposer",
    "get_triangulation_with_diagonals",
    "hertel_mehlhorn",
    "triangulate_polygon",
    "triangulate_polygon_with_holes",
]
