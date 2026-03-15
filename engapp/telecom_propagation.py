"""5G Network Planning and Telecommunications Propagation algorithms."""

import argparse
import math
from typing import Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class TelecomPropagation:
    """Provides algorithms for Line-of-Sight and Fresnel Zone analysis."""

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
    def check_line_of_sight(mesh: TriangleMesh, tx: Point3D, rx: Point3D) -> bool:
        """
        Checks if there is a clear Line-of-Sight (LoS) between transmitter and receiver.
        Returns True if clear, False if blocked by the mesh.
        """
        tx_t = (tx.x, tx.y, getattr(tx, "z", 0.0))
        rx_t = (rx.x, rx.y, getattr(rx, "z", 0.0))

        dx = rx_t[0] - tx_t[0]
        dy = rx_t[1] - tx_t[1]
        dz = rx_t[2] - tx_t[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist < 1e-6:
            return True

        ray_dir = (dx / dist, dy / dist, dz / dist)

        verts = (
            mesh.vertices()
            if hasattr(mesh, "vertices")
            else getattr(mesh, "_vertices", [])
        )
        faces = mesh.faces() if hasattr(mesh, "faces") else getattr(mesh, "_faces", [])

        for face in faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            v0t = (v0.x, v0.y, getattr(v0, "z", 0.0))
            v1t = (v1.x, v1.y, getattr(v1, "z", 0.0))
            v2t = (v2.x, v2.y, getattr(v2, "z", 0.0))

            t = TelecomPropagation._ray_triangle_intersect(tx_t, ray_dir, v0t, v1t, v2t)
            if 0 < t < dist:
                return False  # Blocked

        return True

    @staticmethod
    def fresnel_zone_radius(d1: float, d2: float, frequency_hz: float) -> float:
        """
        Calculates the 1st Fresnel zone radius at a specific point.
        d1: distance from transmitter to point
        d2: distance from point to receiver
        frequency_hz: signal frequency in Hertz
        """
        c = 299792458.0  # speed of light in m/s
        wavelength = c / frequency_hz
        if d1 + d2 == 0:
            return 0.0
        return math.sqrt((wavelength * d1 * d2) / (d1 + d2))


def main():
    parser = argparse.ArgumentParser(description="5G Network Planning and Telecommunications Propagation algorithms.")
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # check_line_of_sight subparser
    los_parser = subparsers.add_parser("los", help="Checks clear Line-of-Sight between transmitter and receiver")
    los_parser.add_argument("--tx", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Transmitter position")
    los_parser.add_argument("--rx", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Receiver position")

    # fresnel_zone_radius subparser
    fresnel_parser = subparsers.add_parser("fresnel", help="Calculates 1st Fresnel zone radius")
    fresnel_parser.add_argument("--d1", type=float, required=True, help="Distance from transmitter to point")
    fresnel_parser.add_argument("--d2", type=float, required=True, help="Distance from point to receiver")
    fresnel_parser.add_argument("--frequency", type=float, required=True, help="Signal frequency in Hertz")

    args = parser.parse_args()
    tools = TelecomPropagation()

    if args.command == "los":
        # Mock a wall for the demo/default
        class MockPoint:
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z

        class MockMesh:
            def vertices(self):
                return [MockPoint(50, -10, 0), MockPoint(50, 10, 0), MockPoint(50, 0, 20)]

            def faces(self):
                return [(0, 1, 2)]

        mesh = MockMesh()
        tx = Point3D(args.tx[0], args.tx[1], args.tx[2])
        rx = Point3D(args.rx[0], args.rx[1], args.rx[2])
        los = tools.check_line_of_sight(mesh, tx, rx)
        print(f"Line of Sight Clear: {los}")
    elif args.command == "fresnel":
        r = tools.fresnel_zone_radius(args.d1, args.d2, args.frequency)
        print(f"1st Fresnel Zone Radius: {r:.2f} meters")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
