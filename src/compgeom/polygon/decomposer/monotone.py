from __future__ import annotations

from compgeom.kernel import EPSILON, Point2D
from .ear_clipping import triangulate_polygon
from .utils import _ordered_face_from_triangles, _share_triangle_edge


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
