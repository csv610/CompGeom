from __future__ import annotations

from collections import Counter
from typing import List, Tuple

from compgeom.kernel import EPSILON, Point2D, cross_product
from compgeom.mesh.mesh import PolygonMesh
from compgeom.polygon.exceptions import UnsupportedAlgorithmError
from compgeom.polygon.line_segment import proper_segment_intersection
from compgeom.polygon.polygon import Polygon


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


def convex_decompose_polygon(
    polygon_input: list[Point2D],
) -> tuple[list[list[int]], list[Point2D]]:
    """Decomposes a simple polygon into convex parts."""
    from .ear_clipping import triangulate_polygon

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


def decompose_polygon(
    polygon: list[Point2D], algorithm: str = "triangulate"
) -> PolygonMesh:
    """Decomposes a simple polygon into simpler pieces using various algorithms."""
    from .ear_clipping import triangulate_polygon
    from .monotone import monotone_decompose_polygon
    from .trapezoidal import trapezoidal_decompose_polygon
    from .visibility import visibility_decompose_polygon

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


def _share_triangle_edge(
    left: list[tuple[int, int, int]], right: list[tuple[int, int, int]]
) -> bool:
    return any(len(set(a).intersection(b)) == 2 for a in left for b in right)


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
