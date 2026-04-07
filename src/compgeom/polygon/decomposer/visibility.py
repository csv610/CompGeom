from __future__ import annotations

from compgeom.kernel import EPSILON, Point2D, cross_product
from compgeom.polygon.line_segment import proper_segment_intersection
from compgeom.polygon.polygon import Polygon
from compgeom.polygon.polygon_path import segment_inside_polygon


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
