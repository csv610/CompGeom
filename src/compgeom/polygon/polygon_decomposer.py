"""Algorithms for decomposing polygons into simpler pieces."""

from __future__ import annotations

from collections import Counter
from typing import List, Tuple
from .polygon import Polygon

from ..kernel import EPSILON, Point2D, contains_point, cross_product, is_on_segment
from ..kernel import distance
from ..mesh.mesh import PolygonMesh
from .line_segment import proper_segment_intersection
from .polygon_utils import ensure_ccw, ensure_cw, point_on_boundary, segment_inside_boundaries


class EarDecomposition:
    """Implements the Ear Clipping algorithm for polygon triangulation."""

    @staticmethod
    def decompose(polygon: list[Point2D], collect_diagonals: bool = False) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point2D]]:
        """Triangulates a simple polygon using ear clipping."""
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


class ConvexDecomposition:
    """Decomposes a simple polygon into convex parts using the Hertel-Mehlhorn algorithm."""

    @staticmethod
    def decompose(polygon_input: list[Point2D]) -> tuple[list[list[int]], list[Point2D]]:
        """Decomposes a simple polygon into convex parts."""
        triangles, diagonals, polygon = EarDecomposition.decompose(polygon_input, collect_diagonals=True)
        partitions = [list(triangle) for triangle in triangles]

        def is_convex(face_indices, vertex_index):
            n = len(face_indices)
            try:
                idx = face_indices.index(vertex_index)
            except ValueError:
                return True
            
            prev_idx = face_indices[(idx - 1) % n]
            next_idx = face_indices[(idx + 1) % n]
            return cross_product(polygon[prev_idx], polygon[vertex_index], polygon[next_idx]) >= -EPSILON

        for diagonal in diagonals:
            u, v = diagonal
            shared_partitions = [
                partition_index
                for partition_index, partition in enumerate(partitions)
                if u in partition and v in partition
            ]
            if len(shared_partitions) != 2:
                continue

            first, second = shared_partitions
            merged_indices = sorted(list(set(partitions[first]) | set(partitions[second])))
            
            if is_convex(merged_indices, u) and is_convex(merged_indices, v):
                partitions.pop(max(first, second))
                partitions.pop(min(first, second))
                partitions.append(merged_indices)

        return partitions, polygon


class MonotoneDecomposition:
    """Decomposes a simple polygon into y-monotone parts."""

    @staticmethod
    def decompose(polygon: list[Point2D]) -> tuple[list[tuple[int, ...]], list[Point2D]]:
        """Decomposes a simple polygon into y-monotone parts."""
        triangles, _, vertices = EarDecomposition.decompose(polygon)
        return _monotone_partitions(triangles, vertices), vertices


class VisibilityDecomposition:
    """Decomposes a simple polygon using reflex-visibility diagonals."""

    @staticmethod
    def decompose(polygon: list[Point2D]) -> tuple[list[tuple[int, ...]], list[Point2D]]:
        """Decomposes a simple polygon into visibility-based parts."""
        ordered = ensure_ccw(list(polygon))
        return _visibility_faces(ordered), ordered


class TrapezoidalDecomposition:
    """Decomposes a simple polygon into vertical trapezoidal cells."""

    @staticmethod
    def decompose(polygon: list[Point2D]) -> list[list[Point2D]]:
        """Decomposes a simple polygon into trapezoids."""
        if len(polygon) < 3:
            return [list(polygon)]
        from .polygon import Polygon
        ordered = Polygon(polygon).ensure_ccw().as_list()
        return _trapezoidal_faces(ordered)


class HoleDecomposition:
    """Triangulates a polygon with holes."""

    @staticmethod
    def decompose(
        outer_boundary: list[Point2D],
        holes: list[list[Point2D]] | None = None,
    ) -> tuple[list[tuple[Point2D, Point2D, Point2D]], list[Point2D]]:
        """Triangulates a polygonal domain with holes."""
        holes = holes or []
        from .polygon import Polygon

        merged_polygon = Polygon(outer_boundary).ensure_ccw()
        for hole in holes:
            merged_polygon = Polygon(_splice_hole(merged_polygon.as_list(), ensure_cw(list(hole))))

        triangle_indices, _, merged_vertices = EarDecomposition.decompose(merged_polygon.as_list())
        triangles = [tuple(merged_vertices[index] for index in triangle) for triangle in triangle_indices]
        return triangles, merged_vertices


class _TriangleView:
    def __init__(self, v1: Point2D, v2: Point2D, v3: Point2D):
        self.vertices = (v1, v2, v3)


def _is_ear(a: Point2D, b: Point2D, c: Point2D, polygon: list[Point2D]) -> bool:
    if cross_product(a, b, c) <= 0:
        return False

    triangle = _TriangleView(a, b, c)
    for point in polygon:
        if point is not a and point is not b and point is not c:
            if contains_point(triangle, point):
                return False
    return True


def _domain_contains_point(outer: list[Point2D], holes: list[list[Point2D]], point: Point2D) -> bool:
    from .polygon import Polygon

    if not Polygon(outer).contains_point(point):
        return False
    return not any(Polygon(hole).contains_point(point) and not point_on_boundary(point, hole) for hole in holes)


def _segment_inside_domain(
    outer: list[Point2D],
    holes: list[list[Point2D]],
    start: Point2D,
    end: Point2D,
    allow_hole_endpoint: Point2D | None = None,
) -> bool:
    return segment_inside_boundaries(
        start,
        end,
        [outer, *holes],
        lambda midpoint: _domain_contains_point(outer, holes, midpoint),
        allow_boundary_endpoint=allow_hole_endpoint,
    )


def _splice_hole(outer: list[Point2D], hole: list[Point2D]) -> list[Point2D]:
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
    merged: list[Point2D] = []
    merged.extend(outer[: outer_index + 1])
    merged.append(hole_vertex)
    merged.extend(rotated_hole[1:])
    merged.append(hole_vertex)
    merged.append(outer_vertex)
    merged.extend(outer[outer_index + 1 :])
    return merged


def _mesh_from_point_faces(point_faces: List[List[Point2D]] | List[tuple[Point2D, ...]]) -> PolygonMesh:
    vertices: list[Point2D] = []
    faces: list[tuple[int, ...]] = []
    vertex_indices: dict[Point2D, int] = {}

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
    vertices: list[Point2D],
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


def _is_y_monotone(face: tuple[int, ...], vertices: list[Point2D]) -> bool:
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
    vertices: list[Point2D],
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


def _point_on_segment_at_x(start: Point2D, end: Point2D, x: float) -> Point2D | None:
    min_x = min(start.x, end.x) - EPSILON
    max_x = max(start.x, end.x) + EPSILON
    if x < min_x or x > max_x:
        return None
    if abs(end.x - start.x) <= EPSILON:
        if abs(start.x - x) > EPSILON:
            return None
        lower, upper = sorted((start, end), key=lambda p: (p.y, p.x))
        return Point2D(x, lower.y if lower.y == upper.y else lower.y)

    t = (x - start.x) / (end.x - start.x)
    y = start.y + t * (end.y - start.y)
    return Point2D(x, y)


def _vertical_line_intersections(polygon: list[Point2D], x: float) -> list[tuple[float, int]]:
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


def _cleanup_face(points: list[Point2D]) -> list[Point2D]:
    face: list[Point2D] = []
    for point in points:
        if face and point == face[-1]:
            continue
        face.append(point)
    if len(face) > 1 and face[0] == face[-1]:
        face.pop()
    return face


def _trapezoidal_faces(polygon: list[Point2D]) -> list[list[Point2D]]:
    x_values = sorted({point.x for point in polygon})
    if len(x_values) < 2:
        return [polygon]

    faces: list[list[Point2D]] = []
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


def _diagonal_crosses(diagonal: tuple[int, int], diagonals: list[tuple[int, int]], polygon: list[Point2D]) -> bool:
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


def _visibility_faces(polygon: list[Point2D]) -> list[tuple[int, ...]]:
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
    """Provides tools to decompose and verify polygon partitions."""

    @staticmethod
    def verify(polygon: list[Point2D], mesh: PolygonMesh) -> bool:
        """
        Verifies if a PolygonMesh is a valid decomposition of the given polygon.
        
        A decomposition is valid if:
        1. Every face is a valid simple polygon with non-zero area.
        2. All faces are oriented consistently with the original polygon.
        3. The faces form a partition: their union is the original polygon and their interiors are disjoint.
        4. All mesh vertices are contained within the original polygon's closure.
        """
        from .polygon_metrics import get_polygon_properties
        from .polygon import Polygon

        # 0. Basic Integrity
        if not mesh.faces:
            return len(polygon) < 3
        
        if any(max(face) >= len(mesh.vertices) or min(face) < 0 for face in mesh.faces):
            return False

        try:
            original_area, _, original_orientation = get_polygon_properties(polygon)
        except Exception:
            return False

        if original_area < EPSILON:
            return not mesh.faces

        original_poly = Polygon(polygon)
        total_mesh_area = 0.0
        face_data = []

        # 1. Individual Face Validation
        for face_indices in mesh.faces:
            if len(face_indices) < 3:
                return False
            
            face_verts = [mesh.vertices[i] for i in face_indices]
            face_area, face_centroid, face_orientation = get_polygon_properties(face_verts)
            
            # Reject degenerate or zero-area faces
            if face_area < EPSILON:
                return False
                
            # Orientation must match original (prevents "inverted" faces covering the same area)
            if face_orientation != original_orientation:
                return False

            # Face Simplicity: Check for self-intersections
            n = len(face_verts)
            for i in range(n):
                p1, p2 = face_verts[i], face_verts[(i + 1) % n]
                for j in range(i + 2, n):
                    if i == 0 and j == n - 1:
                        continue
                    p3, p4 = face_verts[j], face_verts[(j + 1) % n]
                    if proper_segment_intersection(p1, p2, p3, p4):
                        return False

            # Containment: Vertices and interior must be within the original polygon
            for v in face_verts:
                if not original_poly.contains_point(v) and not point_on_boundary(v, polygon):
                    return False
            
            if not original_poly.contains_point(face_centroid):
                return False

            total_mesh_area += face_area
            face_data.append((Polygon(face_verts), face_verts))

        # 2. Area Completeness Check
        # Sum of parts must equal the whole. This implicitly catches gaps or missing pieces.
        if abs(original_area - total_mesh_area) > EPSILON * max(1.0, original_area):
            return False

        # 3. Disjoint Interiors Check (Non-overlapping)
        # For every pair of faces, verify they do not overlap.
        for i in range(len(face_data)):
            poly_i, verts_i = face_data[i]
            for j in range(i + 1, len(face_data)):
                poly_j, verts_j = face_data[j]
                
                # A. Edge Crossing Check: Edges from different faces must not cross.
                for k in range(len(verts_i)):
                    ei1, ei2 = verts_i[k], verts_i[(k + 1) % len(verts_i)]
                    for l in range(len(verts_j)):
                        ej1, ej2 = verts_j[l], verts_j[(l + 1) % len(verts_j)]
                        if proper_segment_intersection(ei1, ei2, ej1, ej2):
                            return False
                
                # B. Interior Containment Check: No vertex of face I should be strictly inside face J.
                for v in verts_i:
                    if poly_j.contains_point(v) and not point_on_boundary(v, verts_j):
                        return False
                
                # C. Reverse Interior Containment Check
                for v in verts_j:
                    if poly_i.contains_point(v) and not point_on_boundary(v, verts_i):
                        return False
                
                # D. Centroid Check: Final catch for identical faces or "nesting" cases 
                # where no vertices are strictly inside (handled by area check, but added for robustness).
                _, centroid_i, _ = get_polygon_properties(verts_i)
                if poly_j.contains_point(centroid_i) and not point_on_boundary(centroid_i, verts_j):
                    return False

        return True


__all__ = [
    "EarDecomposition",
    "ConvexDecomposition",
    "MonotoneDecomposition",
    "VisibilityDecomposition",
    "TrapezoidalDecomposition",
    "HoleDecomposition",
    "PolygonDecomposer",
]
