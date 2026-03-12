"""Incremental Delaunay tetrahedralization using Bowyer-Watson algorithm."""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, Iterable, List, Set, Tuple, Optional, Dict

from ...kernel import (
    EPSILON,
    Point3D,
    tetra_orientation_sign,
    in_sphere,
)
from .utils import PointGrid3D, create_super_tetrahedron

if TYPE_CHECKING:
    from ..mesh import TetMesh

class IncrementalTetrahedron:
    """A tetrahedron in the incremental Delaunay mesh."""
    __slots__ = ("vertices",)

    def __init__(self, v1: Point3D, v2: Point3D, v3: Point3D, v4: Point3D):
        # Ensure positive orientation
        if tetra_orientation_sign(v1, v2, v3, v4) < 0:
            self.vertices = [v1, v2, v4, v3]
        else:
            self.vertices = [v1, v2, v3, v4]

    def contains_in_sphere(self, point: Point3D) -> bool:
        """Checks if the point is inside the circumsphere of the tetrahedron."""
        return in_sphere(self.vertices[0], self.vertices[1], self.vertices[2], self.vertices[3], point)

    def faces(self) -> List[Tuple[Point3D, Point3D, Point3D]]:
        """Returns the four faces of the tetrahedron as tuples of points."""
        v = self.vertices
        # Outward faces for a positively oriented tet:
        # Face 0 (opp v0): (v1, v2, v3)
        # Face 1 (opp v1): (v0, v3, v2)
        # Face 2 (opp v2): (v0, v1, v3)
        # Face 3 (opp v3): (v0, v2, v1)
        return [
            (v[1], v[2], v[3]),
            (v[0], v[3], v[2]),
            (v[0], v[1], v[3]),
            (v[0], v[2], v[1]),
        ]

class IncrementalDelaunayMesher3D:
    """Stateful 3D Incremental Delaunay Mesher using Bowyer-Watson."""
    def __init__(self):
        self.active_tets: set[IncrementalTetrahedron] = set()
        self.super_vertices: set[Point3D] = set()
        self.skipped: list[tuple[Point3D, str]] = []

    def initialize(self, points: Iterable[Point3D]):
        pts = list(points)
        if not pts: return
        
        sv = create_super_tetrahedron(pts)
        self.super_vertices = set(sv)
        root = IncrementalTetrahedron(*sv)
        self.active_tets = {root}

    def add_point(self, p: Point3D):
        bad_tets = []
        for tet in self.active_tets:
            if tet.contains_in_sphere(p):
                bad_tets.append(tet)
        
        if not bad_tets:
            self.skipped.append((p, "Point outside or numerical issue"))
            return

        # Map from canonical face to (actual face, count)
        face_counts: Dict[Tuple[int, ...], Tuple[Tuple[Point3D, Point3D, Point3D], int]] = {}
        for tet in bad_tets:
            for face in tet.faces():
                canonical = tuple(sorted(v.id for v in face))
                if canonical not in face_counts:
                    face_counts[canonical] = (face, 0)
                face_counts[canonical] = (face_counts[canonical][0], face_counts[canonical][1] + 1)

        hole_faces = [face for face, count in face_counts.values() if count == 1]

        # Remove bad tetrahedra
        for tet in bad_tets:
            self.active_tets.remove(tet)

        # Create new tetrahedra from p to each boundary face
        for face in hole_faces:
            try:
                # face is oriented outwards from the removed tets, so (face[0], face[1], face[2], p) 
                # should be positively oriented if p is inside the hole (which it is).
                new_tet = IncrementalTetrahedron(face[0], face[1], face[2], p)
                self.active_tets.add(new_tet)
            except Exception:
                continue

    def get_tets(self) -> list[tuple[Point3D, Point3D, Point3D, Point3D]]:
        final = []
        for t in self.active_tets:
            if not any(v in self.super_vertices for v in t.vertices):
                final.append(tuple(t.vertices))
        return final

    def triangulate(self, points: list[Point3D]) -> tuple[list[tuple[Point3D, Point3D, Point3D, Point3D]], list[tuple[Point3D, str]]]:
        if not points: return [], []

        unique_points = []
        seen = set()
        skipped_initial = []
        for p in points:
            key = (p.x, p.y, p.z)
            if key in seen:
                skipped_initial.append((p, "Duplicate Point"))
                continue
            seen.add(key)
            unique_points.append(p)

        if not unique_points: return [], skipped_initial

        self.initialize(unique_points)
        for p in unique_points:
            self.add_point(p)

        return self.get_tets(), skipped_initial + self.skipped

def triangulate_incremental_3d(points: list[Point3D]) -> tuple[list[tuple[Point3D, Point3D, Point3D, Point3D]], list[tuple[Point3D, str]]]:
    mesher = IncrementalDelaunayMesher3D()
    return mesher.triangulate(points)
