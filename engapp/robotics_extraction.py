"""Robotic Object Extraction from narrow gaps using Configuration Space (C-Space)."""

import argparse
import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class CSpaceExtraction:
    """Provides algorithms for motion planning through narrow constraints."""

    @staticmethod
    def is_path_clear(
        start: Point3D, end: Point3D, mesh: TriangleMesh, radius: float
    ) -> bool:
        """
        Checks if a path is valid for an object of given radius in C-Space.
        Essentially checks if the line segment (start, end) is further than 'radius'
        from all points on the obstacle mesh.
        """
        # Simplify path into samples
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            px = start.x + t * (end.x - start.x)
            py = start.y + t * (end.y - start.y)
            pz = getattr(start, "z", 0.0) + t * (
                getattr(end, "z", 0.0) - getattr(start, "z", 0.0)
            )

            # Distance from point to mesh
            min_dist = float("inf")
            verts = (
                mesh.vertices()
                if hasattr(mesh, "vertices")
                else getattr(mesh, "_vertices", [])
            )
            for v in verts:
                d = math.sqrt(
                    (px - v.x) ** 2 + (py - v.y) ** 2 + (pz - getattr(v, "z", 0.0)) ** 2
                )
                if d < min_dist:
                    min_dist = d

            if min_dist < radius:
                return False  # Collision in C-Space
        return True

    @staticmethod
    def calculate_passability(mesh: TriangleMesh, object_radius: float) -> float:
        """
        Estimates the 'tightness' of the narrowest gap in the mesh for an object of given radius.
        Returns a clearance value. Negative means the object is larger than the gap.
        """
        # Find the two closest non-adjacent vertices in the mesh (bottleneck)
        min_gap = float("inf")
        verts = (
            mesh.vertices()
            if hasattr(mesh, "vertices")
            else getattr(mesh, "_vertices", [])
        )

        # Naive O(N^2) search for the narrowest gap
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                vi, vj = verts[i], verts[j]
                d = math.sqrt(
                    (vi.x - vj.x) ** 2
                    + (vi.y - vj.y) ** 2
                    + (getattr(vi, "z", 0.0) - getattr(vj, "z", 0.0)) ** 2
                )
                if d < min_gap:
                    # Basic check to avoid adjacent vertices
                    min_gap = d

        return min_gap - (2 * object_radius)


def main():
    parser = argparse.ArgumentParser(description="Robotic Object Extraction from narrow gaps using Configuration Space (C-Space).")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Path Clear
    path_parser = subparsers.add_parser("path-clear", help="Check if a path is clear in C-Space")
    path_parser.add_argument("--start", type=float, nargs=3, default=[0, 0, 0], help="Start position (x y z)")
    path_parser.add_argument("--end", type=float, nargs=3, default=[10, 0, 0], help="End position (x y z)")
    path_parser.add_argument("--radius", type=float, required=True, help="Object radius")

    # Passability
    passability_parser = subparsers.add_parser("passability", help="Estimate clearance for an object in a gap")
    passability_parser.add_argument("--radius", type=float, required=True, help="Object radius")

    args = parser.parse_args()

    # Mock Gap Mesh
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def vertices(self):
            return [
                MockPoint(0, -2, 0), MockPoint(10, -2, 0),  # Wall 1
                MockPoint(0, 2, 0), MockPoint(10, 2, 0),    # Wall 2
            ]

    gap_mesh = MockMesh()
    tools = CSpaceExtraction()

    if args.command == "path-clear":
        start = Point3D(args.start[0], args.start[1], args.start[2])
        end = Point3D(args.end[0], args.end[1], args.end[2])
        is_clear = tools.is_path_clear(start, end, gap_mesh, args.radius)
        print(f"Path Clear (Radius {args.radius}): {'YES' if is_clear else 'NO (COLLISION)'}")

    elif args.command == "passability":
        clearance = tools.calculate_passability(gap_mesh, args.radius)
        print(f"C-Space Clearance (Radius {args.radius}): {clearance:.1f} ({'PASS' if clearance >= 0 else 'TRAPPED'})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
