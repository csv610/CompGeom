"""Smart City Visibility and Urban Illumination algorithms."""

import argparse
import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:

    class TriangleMesh:
        def __init__(self, vertices=None, faces=None):
            self.vertices = vertices or []
            self.faces = faces or []

    class Point3D:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x = x
            self.y = y
            self.z = z


class SmartCityVisibility:
    """Provides algorithms for analyzing visibility and light coverage in urban meshes."""

    @staticmethod
    def _ray_triangle_intersect(
        ray_origin: Tuple[float, float, float],
        ray_dir: Tuple[float, float, float],
        v0: Tuple[float, float, float],
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> float:
        """Moller-Trumbore intersection algorithm."""
        eps = 1e-6
        edge1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        edge2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
        h = (
            ray_dir[1] * edge2[2] - ray_dir[2] * edge2[1],
            ray_dir[2] * edge2[0] - ray_dir[0] * edge2[2],
            ray_dir[0] * edge2[1] - ray_dir[1] * edge2[0],
        )
        a = edge1[0] * h[0] + edge1[1] * h[1] + edge1[2] * h[2]

        if -eps < a < eps:
            return -1.0

        f = 1.0 / a
        s = (ray_origin[0] - v0[0], ray_origin[1] - v0[1], ray_origin[2] - v0[2])
        u = f * (s[0] * h[0] + s[1] * h[1] + s[2] * h[2])
        if u < 0.0 or u > 1.0:
            return -1.0

        q = (
            s[1] * edge1[2] - s[2] * edge1[1],
            s[2] * edge1[0] - s[0] * edge1[2],
            s[0] * edge1[1] - s[1] * edge1[0],
        )
        v = f * (ray_dir[0] * q[0] + ray_dir[1] * q[1] + ray_dir[2] * q[2])
        if v < 0.0 or u + v > 1.0:
            return -1.0

        t = f * (edge2[0] * q[0] + edge2[1] * q[1] + edge2[2] * q[2])
        if t > eps:
            return t
        return -1.0

    @staticmethod
    def is_visible(
        mesh: TriangleMesh,
        observer: Tuple[float, float, float],
        target: Tuple[float, float, float],
    ) -> bool:
        """Checks if a target point is visible from an observer position (Line-of-Sight)."""
        dx = target[0] - observer[0]
        dy = target[1] - observer[1]
        dz = target[2] - observer[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist < 1e-6:
            return True

        ray_dir = (dx / dist, dy / dist, dz / dist)

        verts = mesh.vertices if hasattr(mesh, "vertices") else []
        faces = mesh.faces if hasattr(mesh, "faces") else []

        for face in faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            v0t = (v0.x, v0.y, getattr(v0, "z", 0.0))
            v1t = (v1.x, v1.y, getattr(v1, "z", 0.0))
            v2t = (v2.x, v2.y, getattr(v2, "z", 0.0))

            t = SmartCityVisibility._ray_triangle_intersect(
                observer, ray_dir, v0t, v1t, v2t
            )
            # Intersection must be between observer and target (with small epsilon to avoid self-intersection)
            if 1e-4 < t < dist - 1e-4:
                return False
        return True

    @staticmethod
    def calculate_illumination_score(
        mesh: TriangleMesh,
        light_pos: Tuple[float, float, float],
        sample_points: List[Tuple[float, float, float]],
    ) -> float:
        """
        Calculates the percentage of sample points illuminated by a light source.
        Used for optimizing streetlight placement.
        """
        if not sample_points:
            return 0.0

        visible_count = 0
        for p in sample_points:
            if SmartCityVisibility.is_visible(mesh, light_pos, p):
                visible_count += 1

        return (visible_count / len(sample_points)) * 100.0


def main():
    parser = argparse.ArgumentParser(description="Smart City Visibility and Urban Illumination algorithms.")
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # is_visible subparser
    visible_parser = subparsers.add_parser("is-visible", help="Checks if a target point is visible from an observer position")
    visible_parser.add_argument("--observer", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Observer position")
    visible_parser.add_argument("--target", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Target position")

    # illumination subparser
    illum_parser = subparsers.add_parser("illumination", help="Calculates illumination score from a light source")
    illum_parser.add_argument("--light-pos", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Light source position")

    args = parser.parse_args()

    # 1. Mock a simple city block (a "building" box)
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def __init__(self):
            # A building at (4,4) to (6,6) with height 5
            self.vertices = [
                MockPoint(4, 4, 0),
                MockPoint(6, 4, 0),
                MockPoint(6, 6, 0),
                MockPoint(4, 6, 0),  # Base
                MockPoint(4, 4, 5),
                MockPoint(6, 4, 5),
                MockPoint(6, 6, 5),
                MockPoint(4, 6, 5),  # Top
            ]
            self.faces = [
                (0, 1, 5),
                (0, 5, 4),  # South Wall
                (1, 2, 6),
                (1, 6, 5),  # East Wall
                (4, 5, 6),
                (4, 6, 7),  # Roof
            ]

    city_mesh = MockMesh()

    if args.command == "is-visible":
        visible = SmartCityVisibility.is_visible(city_mesh, tuple(args.observer), tuple(args.target))
        print(f"Target {args.target} is visible from {args.observer}: {visible}")
    elif args.command == "illumination":
        # Define target sample points on the ground for the demo
        ground_points = []
        for x in range(0, 11, 2):
            for y in range(0, 11, 2):
                ground_points.append((x, y, 0.0))
        
        score = SmartCityVisibility.calculate_illumination_score(city_mesh, tuple(args.light_pos), ground_points)
        print(f"Illumination score for light at {args.light_pos}: {score:.1f}% coverage")
    else:
        # Default demo if no command provided (though subparsers usually require one if configured that way)
        # However, argparse doesn't require a subparser by default unless you set required=True (Python 3.7+)
        # We can just print help.
        parser.print_help()


if __name__ == "__main__":
    main()

