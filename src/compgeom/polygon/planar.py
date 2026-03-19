"""Planar subdivision primitives built around a lightweight DCEL."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from compgeom.polygon.exceptions import DegeneratePolygonError
from compgeom.polygon.tolerance import EPSILON
from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon


@dataclass
class DCELVertex:
    point: Point2D
    incident_edge: "DCELHalfEdge | None" = None


@dataclass
class DCELFace:
    id: int
    outer_component: "DCELHalfEdge | None" = None
    inner_components: list["DCELHalfEdge"] = field(default_factory=list)
    is_exterior: bool = False

    def cycle_points(self, component_edge: DCELHalfEdge | None = None) -> list[Point2D]:
        start_edge = component_edge or self.outer_component
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

    def contains_point(self, point: Point2D) -> bool:
        if self.is_exterior:
            return False

        outer = self.cycle_points()
        if not outer or not Polygon(outer).contains_point(point):
            return False

        for inner in self.inner_components:
            if Polygon(self.cycle_points(inner)).contains_point(point):
                return False
        return True


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

    @staticmethod
    def _link_cycle(face: DCELFace, points: list[Point2D]) -> tuple[list[DCELVertex], list[DCELHalfEdge], list[DCELHalfEdge]]:
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

    @classmethod
    def from_polygon(cls, outer_boundary: Polygon | Sequence[Point2D], holes: list[Polygon | list[Point2D]] | None = None) -> DCEL:
        outer_poly = outer_boundary if isinstance(outer_boundary, Polygon) else Polygon(outer_boundary)
        outer_ccw = outer_poly.ensure_ccw()
        if len(outer_ccw) < 3:
            raise DegeneratePolygonError("Outer boundary must contain at least 3 vertices.")
        if outer_ccw.area < EPSILON:
            raise DegeneratePolygonError("Outer boundary must have non-zero area.")

        holes = holes or []
        bounded_face = DCELFace(id=0, is_exterior=False)
        exterior_face = DCELFace(id=1, is_exterior=True)

        vertices, interior_edges, exterior_edges = cls._link_cycle(bounded_face, outer_ccw.as_list())
        for edge in exterior_edges:
            edge.face = exterior_face
        exterior_face.outer_component = exterior_edges[0]

        all_vertices = list(vertices)
        all_edges = interior_edges + exterior_edges

        for hole in holes:
            hole_poly = hole if isinstance(hole, Polygon) else Polygon(hole)
            hole_cw = hole_poly.ensure_cw()
            if len(hole_cw) < 3:
                raise DegeneratePolygonError("Each hole must contain at least 3 vertices.")
            if hole_cw.area < EPSILON:
                raise DegeneratePolygonError("Hole boundary must have non-zero area.")
            
            hole_face = DCELFace(id=len([bounded_face, exterior_face]) + len(bounded_face.inner_components))
            hole_vertices, hole_interior, hole_exterior = cls._link_cycle(hole_face, hole_cw.as_list())
            for edge in hole_interior:
                edge.face = exterior_face
            for edge in hole_exterior:
                edge.face = bounded_face
            bounded_face.inner_components.append(hole_exterior[0])
            all_vertices.extend(hole_vertices)
            all_edges.extend(hole_interior)
            all_edges.extend(hole_exterior)

        return cls(vertices=all_vertices, half_edges=all_edges, faces=[bounded_face, exterior_face])

    def locate_face(self, point: Point2D) -> DCELFace:
        for face in self.faces:
            if face.contains_point(point):
                return face
        return next(face for face in self.faces if face.is_exterior)


__all__ = [
    "DCEL",
    "DCELFace",
    "DCELHalfEdge",
    "DCELVertex",
]
