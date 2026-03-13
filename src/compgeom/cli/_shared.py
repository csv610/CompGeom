from __future__ import annotations

import sys
from collections.abc import Iterable, Sequence

from compgeom import Point2D


def read_stdin_lines() -> list[str]:
    return sys.stdin.readlines()


def read_nonempty_stdin_lines() -> list[str]:
    return [line.strip() for line in sys.stdin if line.strip()]


def print_lines(lines: Iterable[str]) -> None:
    for line in lines:
        print(line)


def parse_points(lines: Iterable[str], *, with_ids: bool = False) -> list[Point2D]:
    points: list[Point2D] = []
    for line in lines:
        point = parse_point_line(line, point_id=len(points) if not with_ids else None, with_id=with_ids)
        if point is not None:
            points.append(point)
    return points


def parse_point_line(
    line: str,
    *,
    point_id: int | None = None,
    with_id: bool = False,
) -> Point2D | None:
    return parse_point_fields(line.strip().split(), point_id=point_id, with_id=with_id)


def parse_point_fields(
    fields: Sequence[str],
    *,
    point_id: int | None = None,
    with_id: bool = False,
) -> Point2D | None:
    expected = 3 if with_id else 2
    if len(fields) < expected:
        return None

    try:
        if with_id:
            return Point2D(float(fields[1]), float(fields[2]), int(fields[0]))
        if point_id is None:
            return Point2D(float(fields[0]), float(fields[1]))
        return Point2D(float(fields[0]), float(fields[1]), point_id)
    except ValueError:
        return None


def format_point(point: Point2D) -> str:
    return f"({point.x:.6f}, {point.y:.6f})"


def demo_points() -> list[Point2D]:
    coordinates = [
        (0.0, 0.0),
        (2.0, 1.0),
        (1.0, 3.0),
        (-1.0, 2.0),
        (3.5, 2.5),
        (2.25, 2.0),
    ]
    return [Point2D(x, y, index) for index, (x, y) in enumerate(coordinates)]


def demo_polygon() -> list[Point2D]:
    coordinates = [
        (0.0, 0.0),
        (5.0, 0.0),
        (6.0, 2.0),
        (4.0, 5.0),
        (1.5, 4.0),
        (-1.0, 2.0),
    ]
    return [Point2D(x, y, index) for index, (x, y) in enumerate(coordinates)]


def demo_mesh_lines() -> list[str]:
    return [
        "0 0 0\n",
        "1 1 0\n",
        "2 0 1\n",
        "3 1 1\n",
        "T\n",
        "0 1 2\n",
        "1 3 2\n",
    ]
