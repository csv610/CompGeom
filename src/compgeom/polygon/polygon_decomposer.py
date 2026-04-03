from __future__ import annotations
from compgeom.polygon.polygon_path import segment_inside_polygon

"""Algorithms for decomposing polygons into simpler pieces."""


import math
from collections import Counter
from typing import List, Tuple, Sequence

from compgeom.kernel import EPSILON, Point2D, contains_point, cross_product, distance
from compgeom.mesh.mesh import PolygonMesh
from compgeom.polygon.exceptions import HoleConnectionError, UnsupportedAlgorithmError
from compgeom.polygon.line_segment import proper_segment_intersection
from compgeom.polygon.polygon import Polygon


def is_ear(a: Point2D, b: Point2D, c: Point2D, polygon: Sequence[Point2D]) -> bool:
    """Check if the triangle (a, b, c) is an ear of the polygon."""
    if cross_product(a, b, c) <= 0:
        return False

    class TriangleView:
        def __init__(self, v1: Point2D, v2: Point2D, v3: Point2D):
            self.vertices = (v1, v2, v3)

    triangle = TriangleView(a, b, c)
    for point in polygon:
        if point is not a and point is not b and point is not c:
            if contains_point(triangle, point):
                return False
    return True


def mesh_from_point_faces(
    point_faces: List[List[Point2D]] | List[tuple[Point2D, ...]],
) -> PolygonMesh:
    """Create a PolygonMesh from a list of point-based faces."""
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


def triangulate_polygon(
    polygon: list[Point2D], collect_diagonals: bool = False
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]], list[Point2D]]:
    """Triangulates a simple polygon using ear clipping."""
    poly_obj = Polygon(polygon).ensure_ccw()
    ordered = poly_obj.as_list()
    polygon_size = len(ordered)
    working_polygon = list(ordered)
    working_indices = list(range(polygon_size))
    triangles: list[tuple[int, int, int]] = []
    diagonals: list[tuple[int, int]] = []

    while len(working_indices) > 3:
        for offset, current in enumerate(working_indices):
            prev_index = working_indices[offset - 1]
            next_index = working_indices[(offset + 1) % len(working_indices)]
            if not is_ear(
                ordered[prev_index],
                ordered[current],
                ordered[next_index],
                working_polygon,
            ):
                continue

            triangles.append((prev_index, current, next_index))
            if (
                collect_diagonals
                and abs(next_index - prev_index) != 1
                and {prev_index, next_index}
                != {
                    0,
                    polygon_size - 1,
                }
            ):
                diagonals.append(tuple(sorted((prev_index, next_index))))
            working_indices.pop(offset)
            working_polygon.pop(offset)
            break
        else:
            break

    if len(working_indices) == 3:
        triangles.append(tuple(working_indices))

    return triangles, diagonals, ordered


def convex_decompose_polygon(
    polygon_input: list[Point2D],
) -> tuple[list[list[int]], list[Point2D]]:
    """Decomposes a simple polygon into convex parts."""
    triangles, diagonals, polygon = triangulate_polygon(
        polygon_input, collect_diagonals=True
    )
    partitions = [list(triangle) for triangle in triangles]

    def _is_convex(face_indices, vertex_index):
        n = len(face_indices)
        try:
            idx = face_indices.index(vertex_index)
        except ValueError:
            return True

        prev_idx = face_indices[(idx - 1) % n]
        next_idx = face_indices[(idx + 1) % n]
        return (
            cross_product(polygon[prev_idx], polygon[vertex_index], polygon[next_idx])
            >= -EPSILON
        )

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

        if _is_convex(merged_indices, u) and _is_convex(merged_indices, v):
            partitions.pop(max(first, second))
            partitions.pop(min(first, second))
            partitions.append(merged_indices)

    return partitions, polygon


def monotone_decompose_polygon(
    polygon: list[Point2D],
) -> tuple[list[tuple[int, ...]], list[Point2D]]:
    """Decomposes a simple polygon into y-monotone parts."""
    triangles, _, vertices = triangulate_polygon(polygon)
    return _monotone_partitions(triangles, vertices), vertices


def _monotone_partitions(
    triangles: list[tuple[int, int, int]],
    vertices: list[Point2D],
) -> list[tuple[int, ...]]:
    partitions = [
        {"triangles": [triangle], "face": tuple(triangle)} for triangle in triangles
    ]

    changed = True
    while changed:
        changed = False
        for i in range(len(partitions)):
            for j in range(i + 1, len(partitions)):
                if not _share_triangle_edge(
                    partitions[i]["triangles"], partitions[j]["triangles"]
                ):
                    continue

                merged_triangles = (
                    partitions[i]["triangles"] + partitions[j]["triangles"]
                )
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


def _share_triangle_edge(
    left: list[tuple[int, int, int]], right: list[tuple[int, int, int]]
) -> bool:
    return any(len(set(a).intersection(b)) == 2 for a in left for b in right)


def _is_y_monotone(face: tuple[int, ...], vertices: list[Point2D]) -> bool:
    if len(face) <= 3:
        return True

    top = max(
        range(len(face)), key=lambda i: (vertices[face[i]].y, -vertices[face[i]].x)
    )
    bottom = min(
        range(len(face)), key=lambda i: (vertices[face[i]].y, vertices[face[i]].x)
    )

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


def visibility_decompose_polygon(
    polygon: list[Point2D],
) -> tuple[list[tuple[int, ...]], list[Point2D]]:
    """Decomposes a simple polygon into visibility-based parts."""
    poly_obj = Polygon(polygon).ensure_ccw()
    ordered = poly_obj.as_list()
    return _visibility_faces(ordered), ordered


def _visibility_faces(polygon: list[Point2D]) -> list[tuple[int, ...]]:
    poly = Polygon(polygon)
    n = len(polygon)
    reflex_indices = [
        i
        for i in range(n)
        if cross_product(polygon[i - 1], polygon[i], polygon[(i + 1) % n]) < -EPSILON
    ]

    chosen: list[tuple[int, int]] = []
    for reflex in reflex_indices:
        candidates: list[tuple[float, tuple[int, int]]] = []
        for target in range(n):
            if target == reflex:
                continue
            if target in {(reflex - 1) % n, (reflex + 1) % n}:
                continue
            if not segment_inside_polygon(poly, polygon[reflex], polygon[target]):
                continue
            diagonal = tuple(sorted((reflex, target)))
            if diagonal in chosen or _diagonal_crosses(diagonal, chosen, polygon):
                continue
            dx = polygon[reflex].x - polygon[target].x
            dy = polygon[reflex].y - polygon[target].y
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


def _diagonal_crosses(
    diagonal: tuple[int, int], diagonals: list[tuple[int, int]], polygon: list[Point2D]
) -> bool:
    a, b = diagonal
    for c, d in diagonals:
        if {a, b}.intersection({c, d}):
            continue
        if proper_segment_intersection(polygon[a], polygon[b], polygon[c], polygon[d]):
            return True
    return False


def _split_face_by_diagonal(
    face: tuple[int, ...], diagonal: tuple[int, int]
) -> list[tuple[int, ...]] | None:
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

    first = face[ia : ib + 1]
    second = face[ib:] + face[: ia + 1]
    if len(first) < 3 or len(second) < 3:
        return None
    return [tuple(first), tuple(second)]


def trapezoidal_decompose_polygon(polygon: list[Point2D]) -> list[list[Point2D]]:
    """Decomposes a simple polygon into trapezoids."""
    if len(polygon) < 3:
        return [list(polygon)]
    ordered = Polygon(polygon).ensure_ccw().as_list()

    x_values = sorted({point.x for point in ordered})
    if len(x_values) < 2:
        return [ordered]

    faces: list[list[Point2D]] = []
    for left_x, right_x in zip(x_values, x_values[1:]):
        if right_x - left_x <= EPSILON:
            continue
        mid_x = (left_x + right_x) / 2.0
        intersections = _vertical_line_intersections(ordered, mid_x)
        for lower_hit, upper_hit in zip(intersections[0::2], intersections[1::2]):
            _, lower_edge_index = lower_hit
            _, upper_edge_index = upper_hit
            lower_start = ordered[lower_edge_index]
            lower_end = ordered[(lower_edge_index + 1) % len(ordered)]
            upper_start = ordered[upper_edge_index]
            upper_end = ordered[(upper_edge_index + 1) % len(ordered)]

            lower_left = _point_on_segment_at_x(lower_start, lower_end, left_x)
            lower_right = _point_on_segment_at_x(lower_start, lower_end, right_x)
            upper_left = _point_on_segment_at_x(upper_start, upper_end, left_x)
            upper_right = _point_on_segment_at_x(upper_start, upper_end, right_x)
            if None in (lower_left, lower_right, upper_left, upper_right):
                continue

            face = _cleanup_face([lower_left, lower_right, upper_right, upper_left])
            if len(face) >= 3:
                faces.append(face)

    return faces or [ordered]


def _vertical_line_intersections(
    polygon: list[Point2D], x: float
) -> list[tuple[float, int]]:
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


def _point_on_segment_at_x(start: Point2D, end: Point2D, x: float) -> Point2D | None:
    """
    Compute the point on a segment at a given x-coordinate.
    Returns None if x is outside the segment's x-range.
    """
    min_x = min(start.x, end.x) - EPSILON
    max_x = max(start.x, end.x) + EPSILON
    if x < min_x or x > max_x:
        return None
    if abs(end.x - start.x) <= EPSILON:
        if abs(start.x - x) > EPSILON:
            return None
        return Point2D(x, start.y)

    t = (x - start.x) / (end.x - start.x)
    y = start.y + t * (end.y - start.y)
    return Point2D(x, y)


def _cleanup_face(points: list[Point2D]) -> list[Point2D]:
    face: list[Point2D] = []
    for point in points:
        if face and point == face[-1]:
            continue
        face.append(point)
    if len(face) > 1 and face[0] == face[-1]:
        face.pop()
    return face


def triangulate_polygon_with_holes(
    outer_boundary: list[Point2D],
    holes: list[list[Point2D]] | None = None,
) -> tuple[list[tuple[Point2D, Point2D, Point2D]], list[Point2D]]:
    """Triangulates a polygonal domain with holes."""
    holes = holes or []
    merged_polygon = Polygon(outer_boundary).ensure_ccw()
    for hole in holes:
        merged_polygon = Polygon(
            _splice_hole(merged_polygon.as_list(), Polygon(hole).ensure_cw().as_list())
        )

    triangle_indices, _, merged_vertices = triangulate_polygon(merged_polygon.as_list())
    triangles = [
        tuple(merged_vertices[index] for index in triangle)
        for triangle in triangle_indices
    ]
    return triangles, merged_vertices


def _splice_hole(outer: list[Point2D], hole: list[Point2D]) -> list[Point2D]:
    hole_vertex_index = max(
        range(len(hole)), key=lambda index: (hole[index].x, -hole[index].y)
    )
    hole_vertex = hole[hole_vertex_index]

    candidates = []
    for outer_index, outer_vertex in enumerate(outer):
        if not _segment_inside_domain(
            outer, [hole], hole_vertex, outer_vertex, allow_hole_endpoint=hole_vertex
        ):
            continue
        candidates.append((distance(hole_vertex, outer_vertex), outer_index))
    if not candidates:
        raise HoleConnectionError("Failed to connect hole to outer boundary.")

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


def _segment_inside_domain(
    outer: list[Point2D],
    holes: list[list[Point2D]],
    start: Point2D,
    end: Point2D,
    allow_hole_endpoint: Point2D | None = None,
) -> bool:
    from compgeom.polygon.polygon_utils import segment_inside_boundaries

    return segment_inside_boundaries(
        start,
        end,
        [outer, *holes],
        lambda midpoint: _domain_contains_point(outer, holes, midpoint),
        allow_boundary_endpoint=allow_hole_endpoint,
    )


def _domain_contains_point(
    outer: list[Point2D], holes: list[list[Point2D]], point: Point2D
) -> bool:
    if not Polygon(outer).contains_point(point):
        return False
    return not any(
        Polygon(hole).contains_point(point)
        and not Polygon(hole).point_on_boundary(point)
        for hole in holes
    )


def decompose_polygon(
    polygon: list[Point2D], algorithm: str = "triangulate"
) -> PolygonMesh:
    """Decomposes a simple polygon into simpler pieces using various algorithms."""
    algo_map = {
        "triangulate": lambda p: PolygonMesh(
            triangulate_polygon(p)[2], [tuple(f) for f in triangulate_polygon(p)[0]]
        ),
        "ear": lambda p: PolygonMesh(
            triangulate_polygon(p)[2], [tuple(f) for f in triangulate_polygon(p)[0]]
        ),
        "convex": lambda p: PolygonMesh(
            convex_decompose_polygon(p)[1],
            [tuple(f) for f in convex_decompose_polygon(p)[0]],
        ),
        "monotone": lambda p: PolygonMesh(
            monotone_decompose_polygon(p)[1],
            [tuple(f) for f in monotone_decompose_polygon(p)[0]],
        ),
        "trapezoidal": lambda p: mesh_from_point_faces(
            trapezoidal_decompose_polygon(p)
        ),
        "visibility": lambda p: PolygonMesh(
            visibility_decompose_polygon(p)[1],
            [tuple(f) for f in visibility_decompose_polygon(p)[0]],
        ),
    }

    normalized_algo = algorithm.lower().replace("_", "")
    func = algo_map.get(normalized_algo)
    if not func:
        raise UnsupportedAlgorithmError(
            f"Unsupported decomposition algorithm: {algorithm}. Supported: {list(algo_map.keys())}"
        )

    return func(polygon)


def verify_polygon_decomposition(polygon: list[Point2D], mesh: PolygonMesh) -> bool:
    """
    Verifies if a PolygonMesh is a valid decomposition of the given polygon.
    """
    if not mesh.faces:
        return len(polygon) < 3

    if any(max(face) >= len(mesh.vertices) or min(face) < 0 for face in mesh.faces):
        return False

    poly_obj = Polygon(polygon)
    props = poly_obj.properties()
    original_area = props.area
    original_orientation = props.orientation

    if original_area < EPSILON:
        return not mesh.faces

    total_mesh_area = 0.0
    face_data = []

    for face_indices in mesh.faces:
        if len(face_indices) < 3:
            return False

        face_verts = [mesh.vertices[i] for i in face_indices]
        face_poly = Polygon(face_verts)
        face_props = face_poly.properties()

        if face_props.area < EPSILON:
            return False

        if face_props.orientation != original_orientation:
            return False

        n = len(face_verts)
        for i in range(n):
            p1, p2 = face_verts[i], face_verts[(i + 1) % n]
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                p3, p4 = face_verts[j], face_verts[(j + 1) % n]
                if proper_segment_intersection(p1, p2, p3, p4):
                    return False

        for v in face_verts:
            if not poly_obj.contains_point(v) and not poly_obj.point_on_boundary(v):
                return False

        if not poly_obj.contains_point(face_props.centroid):
            return False

        total_mesh_area += face_props.area
        face_data.append((face_poly, face_verts))

    if abs(original_area - total_mesh_area) > EPSILON * max(1.0, original_area):
        return False

    for i in range(len(face_data)):
        poly_i, verts_i = face_data[i]
        for j in range(i + 1, len(face_data)):
            poly_j, verts_j = face_data[j]

            for k in range(len(verts_i)):
                ei1, ei2 = verts_i[k], verts_i[(k + 1) % len(verts_i)]
                for l in range(len(verts_j)):
                    ej1, ej2 = verts_j[l], verts_j[(l + 1) % len(verts_j)]
                    if proper_segment_intersection(ei1, ei2, ej1, ej2):
                        return False

            for v in verts_i:
                if poly_j.contains_point(v) and not poly_j.point_on_boundary(v):
                    return False

            for v in verts_j:
                if poly_i.contains_point(v) and not poly_i.point_on_boundary(v):
                    return False

            centroid_i = poly_i.properties().centroid
            if poly_j.contains_point(centroid_i) and not poly_j.point_on_boundary(
                centroid_i
            ):
                return False

    return True


__all__ = [
    "triangulate_polygon",
    "convex_decompose_polygon",
    "monotone_decompose_polygon",
    "visibility_decompose_polygon",
    "trapezoidal_decompose_polygon",
    "triangulate_polygon_with_holes",
    "decompose_polygon",
    "verify_polygon_decomposition",
]
