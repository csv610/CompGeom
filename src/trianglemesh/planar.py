"""Planar subdivision primitives built around a lightweight DCEL."""

from __future__ import annotations

from dataclasses import dataclass, field

from .geometry import EPSILON, Point
from .polygon import is_point_in_polygon


@dataclass
class DCELVertex:
    point: Point
    incident_edge: "DCELHalfEdge | None" = None


@dataclass
class DCELFace:
    id: int
    outer_component: "DCELHalfEdge | None" = None
    inner_components: list["DCELHalfEdge"] = field(default_factory=list)
    is_exterior: bool = False


@dataclass
class DCELHalfEdge:
    origin: DCELVertex
    twin: "DCELHalfEdge | None" = None
    next: "DCELHalfEdge | None" = None
    prev: "DCELHalfEdge | None" = None
    face: DCELFace | None = None

    @property
    def destination(self) -> DCELVertex | None:
        return self.next.origin if self.next is not None else None


@dataclass
class DCEL:
    vertices: list[DCELVertex]
    half_edges: list[DCELHalfEdge]
    faces: list[DCELFace]


def _signed_area_twice(polygon: list[Point]) -> float:
    return sum(
        polygon[i].x * polygon[(i + 1) % len(polygon)].y
        - polygon[(i + 1) % len(polygon)].x * polygon[i].y
        for i in range(len(polygon))
    )


def _ensure_orientation(polygon: list[Point], ccw: bool) -> list[Point]:
    area = _signed_area_twice(polygon)
    if ccw and area < 0:
        return list(reversed(polygon))
    if not ccw and area > 0:
        return list(reversed(polygon))
    return list(polygon)


def _link_cycle(face: DCELFace, points: list[Point]) -> tuple[list[DCELVertex], list[DCELHalfEdge], list[DCELHalfEdge]]:
    vertices = [DCELVertex(point) for point in points]
    interior = [DCELHalfEdge(vertex) for vertex in vertices]
    exterior = [DCELHalfEdge(vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]

    for i in range(len(vertices)):
        interior[i].twin = exterior[i]
        exterior[i].twin = interior[i]
        interior[i].face = face
        vertices[i].incident_edge = interior[i]

    for i in range(len(vertices)):
        interior[i].next = interior[(i + 1) % len(vertices)]
        interior[i].prev = interior[(i - 1) % len(vertices)]
        exterior[i].next = exterior[(i - 1) % len(vertices)]
        exterior[i].prev = exterior[(i + 1) % len(vertices)]

    face.outer_component = interior[0]
    return vertices, interior, exterior


def build_polygon_dcel(outer_boundary: list[Point], holes: list[list[Point]] | None = None) -> DCEL:
    if len(outer_boundary) < 3:
        raise ValueError("Outer boundary must contain at least 3 vertices.")

    holes = holes or []
    outer = _ensure_orientation(outer_boundary, ccw=True)
    if abs(_signed_area_twice(outer)) < EPSILON:
        raise ValueError("Outer boundary must have non-zero area.")

    bounded_face = DCELFace(id=0, is_exterior=False)
    exterior_face = DCELFace(id=1, is_exterior=True)

    vertices, interior_edges, exterior_edges = _link_cycle(bounded_face, outer)
    for edge in exterior_edges:
        edge.face = exterior_face
    exterior_face.outer_component = exterior_edges[0]

    all_vertices = list(vertices)
    all_edges = interior_edges + exterior_edges

    for hole in holes:
        if len(hole) < 3:
            raise ValueError("Each hole must contain at least 3 vertices.")
        hole_cycle = _ensure_orientation(hole, ccw=False)
        if abs(_signed_area_twice(hole_cycle)) < EPSILON:
            raise ValueError("Hole boundary must have non-zero area.")
        hole_face = DCELFace(id=len([bounded_face, exterior_face]) + len(bounded_face.inner_components))
        hole_vertices, hole_interior, hole_exterior = _link_cycle(hole_face, hole_cycle)
        for edge in hole_interior:
            edge.face = exterior_face
        for edge in hole_exterior:
            edge.face = bounded_face
        bounded_face.inner_components.append(hole_exterior[0])
        all_vertices.extend(hole_vertices)
        all_edges.extend(hole_interior)
        all_edges.extend(hole_exterior)

    return DCEL(vertices=all_vertices, half_edges=all_edges, faces=[bounded_face, exterior_face])


def face_cycle_points(start_edge: DCELHalfEdge | None) -> list[Point]:
    if start_edge is None:
        return []
    points = []
    edge = start_edge
    while True:
        points.append(edge.origin.point)
        edge = edge.next
        if edge is None or edge is start_edge:
            break
    return points


def face_contains_point(face: DCELFace, point: Point) -> bool:
    if face.is_exterior:
        return False

    outer = face_cycle_points(face.outer_component)
    if not outer or not is_point_in_polygon(point, outer):
        return False

    for inner in face.inner_components:
        if is_point_in_polygon(point, face_cycle_points(inner)):
            return False
    return True


def locate_face(dcel: DCEL, point: Point) -> DCELFace:
    for face in dcel.faces:
        if face_contains_point(face, point):
            return face
    return next(face for face in dcel.faces if face.is_exterior)


__all__ = [
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
    "build_polygon_dcel",
    "face_contains_point",
    "face_cycle_points",
    "locate_face",
]
