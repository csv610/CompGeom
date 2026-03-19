"""Surgical Planning and Computer-Assisted Surgery (CAS) algorithms."""

import argparse
import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriMesh = object
    Point3D = object


class SurgicalPlanning:
    """Provides algorithms for pre-operative planning and surgical guidance."""

    @staticmethod
    def _dist_point_to_segment(
        p: Tuple[float, float, float],
        s0: Tuple[float, float, float],
        s1: Tuple[float, float, float],
    ) -> float:
        """Calculates the minimum distance from a point p to a line segment [s0, s1]."""
        dx, dy, dz = s1[0] - s0[0], s1[1] - s0[1], s1[2] - s0[2]
        l2 = dx * dx + dy * dy + dz * dz
        if l2 == 0:
            return math.sqrt(
                (p[0] - s0[0]) ** 2 + (p[1] - s0[1]) ** 2 + (p[2] - s0[2]) ** 2
            )

        t = ((p[0] - s0[0]) * dx + (p[1] - s0[1]) * dy + (p[2] - s0[2]) * dz) / l2
        t = max(0, min(1, t))

        proj = (s0[0] + t * dx, s0[1] + t * dy, s0[2] + t * dz)
        return math.sqrt(
            (p[0] - proj[0]) ** 2 + (p[1] - proj[1]) ** 2 + (p[2] - proj[2]) ** 2
        )

    @staticmethod
    def safety_margin_analysis(
        critical_structure: TriMesh,
        drill_path_start: Point3D,
        drill_path_end: Point3D,
    ) -> float:
        """
        Calculates the minimum distance between a drill path (line segment)
        and a critical structure (e.g., a nerve or blood vessel mesh).
        Useful for pre-operative safety checks.
        """
        s0 = (
            drill_path_start.x,
            drill_path_start.y,
            getattr(drill_path_start, "z", 0.0),
        )
        s1 = (drill_path_end.x, drill_path_end.y, getattr(drill_path_end, "z", 0.0))

        min_dist = float("inf")

        verts = (
            critical_structure.vertices()
            if hasattr(critical_structure, "vertices")
            else getattr(critical_structure, "_vertices", [])
        )
        # Sample the mesh vertices for a rough safety estimate
        # (For production, a segment-triangle distance algorithm should be used)
        for v in verts:
            vt = (v.x, v.y, getattr(v, "z", 0.0))
            dist = SurgicalPlanning._dist_point_to_segment(vt, s0, s1)
            if dist < min_dist:
                min_dist = dist

        return min_dist

    @staticmethod
    def project_onto_bone(
        point: Point3D, bone_mesh: TriMesh
    ) -> Tuple[Point3D, float]:
        """
        Finds the closest point on the bone surface mesh to a surgical instrument.
        Used for real-time tracking and robotic navigation.
        """
        p_t = (point.x, point.y, getattr(point, "z", 0.0))

        min_dist = float("inf")
        closest_p = Point3D(0, 0, 0)

        verts = (
            bone_mesh.vertices()
            if hasattr(bone_mesh, "vertices")
            else getattr(bone_mesh, "_vertices", [])
        )
        faces = (
            bone_mesh.faces()
            if hasattr(bone_mesh, "faces")
            else getattr(bone_mesh, "_faces", [])
        )

        for face in faces:
            # Check face centroid as a proxy for the closest point
            v0, v1, v2 = [verts[idx] for idx in face]
            centroid = (
                (v0.x + v1.x + v2.x) / 3.0,
                (v0.y + v1.y + v2.y) / 3.0,
                (getattr(v0, "z", 0.0) + getattr(v1, "z", 0.0) + getattr(v2, "z", 0.0))
                / 3.0,
            )

            d2 = (
                (p_t[0] - centroid[0]) ** 2
                + (p_t[1] - centroid[1]) ** 2
                + (p_t[2] - centroid[2]) ** 2
            )
            if d2 < min_dist:
                min_dist = d2
                closest_p = Point3D(centroid[0], centroid[1], centroid[2])

        return closest_p, math.sqrt(min_dist)


def main():
    parser = argparse.ArgumentParser(description="Surgical Planning and Computer-Assisted Surgery (CAS) algorithms.")
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # safety_margin_analysis subparser
    safety_parser = subparsers.add_parser("safety-margin", help="Calculates safety margin from a drill path to a critical structure")
    safety_parser.add_argument("--start", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Drill path start")
    safety_parser.add_argument("--end", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Drill path end")

    # project_onto_bone subparser
    project_parser = subparsers.add_parser("project", help="Projects a point onto the bone surface")
    project_parser.add_argument("--point", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Point to project")

    args = parser.parse_args()

    # Mock a "Nerve" mesh (a simple line of triangles) for demo/default
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def vertices(self):
            return [MockPoint(10, 10, z) for z in range(5)]

        def faces(self):
            return [(0, 1, 2), (1, 2, 3)]

    nerve = MockMesh()
    tools = SurgicalPlanning()

    if args.command == "safety-margin":
        start = Point3D(args.start[0], args.start[1], args.start[2])
        end = Point3D(args.end[0], args.end[1], args.end[2])
        margin = tools.safety_margin_analysis(nerve, start, end)
        print(f"Drill Path Safety Margin: {margin:.2f} mm")
        if margin < 2.0:
            print("WARNING: Path too close to critical structure!")
        else:
            print("Path is SAFE.")
    elif args.command == "project":
        point = Point3D(args.point[0], args.point[1], args.point[2])
        closest, dist = tools.project_onto_bone(point, nerve)
        print(f"Closest Surface Point: ({closest.x}, {closest.y}, {getattr(closest, 'z', 0.0)})")
        print(f"Distance to Surface: {dist:.2f} mm")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
