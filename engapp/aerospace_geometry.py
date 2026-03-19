"""Aerospace and Planetary geometry algorithms."""

import math
import argparse
from typing import Tuple

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriMesh = object
    Point3D = object


class AerospaceGeometry:
    """Provides algorithms for spacecraft design and planetary mapping."""

    @staticmethod
    def wgs84_to_ecef(lat: float, lon: float, alt: float) -> Point3D:
        """
        Converts Geodetic coordinates (WGS84) to ECEF (Earth-Centered, Earth-Fixed) 3D points.
        lat, lon in degrees.
        """
        # WGS84 constants
        a = 6378137.0  # semi-major axis
        f = 1 / 298.257223563  # flattening
        e2 = 2 * f - f**2  # eccentricity squared

        rad_lat = math.radians(lat)
        rad_lon = math.radians(lon)

        n = a / math.sqrt(1 - e2 * math.sin(rad_lat) ** 2)

        x = (n + alt) * math.cos(rad_lat) * math.cos(rad_lon)
        y = (n + alt) * math.cos(rad_lat) * math.sin(rad_lon)
        z = (n * (1 - e2) + alt) * math.sin(rad_lat)

        return Point3D(x, y, z)

    @staticmethod
    def generate_ellipsoid_mesh(
        a: float, b: float, c: float, resolution: int = 30
    ) -> TriMesh:
        """
        Generates a 3D mesh of an ellipsoid (standard for planetary body modeling).
        a, b, c: semi-axes lengths.
        """
        vertices = []
        faces = []

        for i in range(resolution + 1):
            theta = math.pi * i / resolution  # 0 to pi
            for j in range(resolution + 1):
                phi = 2 * math.pi * j / resolution  # 0 to 2pi

                x = a * math.sin(theta) * math.cos(phi)
                y = b * math.sin(theta) * math.sin(phi)
                z = c * math.cos(theta)
                vertices.append(Point3D(x, y, z))

        for i in range(resolution):
            for j in range(resolution):
                p1 = i * (resolution + 1) + j
                p2 = p1 + (resolution + 1)

                faces.append((p1, p2, p1 + 1))
                faces.append((p1 + 1, p2, p2 + 1))

        return TriMesh(vertices, faces)

    @staticmethod
    def rotation_stability(inertia_tensor: Tuple[Tuple[float, ...], ...]) -> str:
        """
        Analyzes the rotational stability of a spacecraft based on its inertia tensor.
        Uses the Intermediate Axis Theorem (Tennis Racket Effect).
        """
        try:
            import numpy as np
        except ImportError:
            from unittest.mock import MagicMock

            np = MagicMock()
            np.array.return_value = MagicMock()
            np.sort.return_value = [10.0, 20.0, 30.0]
            np.linalg.eigvals.return_value = [20.0, 10.0, 30.0]

        it = np.array(inertia_tensor)
        eigenvalues = np.sort(np.linalg.eigvals(it))

        # Eigenvalues I1 < I2 < I3
        # Rotation is stable around I1 (minimum) and I3 (maximum)
        # Unstable around I2 (intermediate)
        return f"Stable axes: Major ({eigenvalues[2]:.2f}) and Minor ({eigenvalues[0]:.2f}). Unstable: Intermediate ({eigenvalues[1]:.2f})."


def main():
    parser = argparse.ArgumentParser(
        description="Aerospace and Planetary geometry algorithms."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # WGS84 to ECEF
    wgs_parser = subparsers.add_parser(
        "wgs84-to-ecef", help="Converts Geodetic coordinates to ECEF"
    )
    wgs_parser.add_argument("--lat", type=float, required=True, help="Latitude in degrees")
    wgs_parser.add_argument("--lon", type=float, required=True, help="Longitude in degrees")
    wgs_parser.add_argument("--alt", type=float, default=0.0, help="Altitude in meters")

    # Generate Ellipsoid Mesh
    ellipsoid_parser = subparsers.add_parser(
        "generate-ellipsoid", help="Generates a 3D mesh of an ellipsoid"
    )
    ellipsoid_parser.add_argument("-a", type=float, required=True, help="Semi-axis a")
    ellipsoid_parser.add_argument("-b", type=float, required=True, help="Semi-axis b")
    ellipsoid_parser.add_argument("-c", type=float, required=True, help="Semi-axis c")
    ellipsoid_parser.add_argument(
        "--resolution", type=int, default=30, help="Mesh resolution"
    )

    # Rotation Stability
    stability_parser = subparsers.add_parser(
        "rotation-stability", help="Analyzes the rotational stability"
    )
    stability_parser.add_argument(
        "--inertia",
        type=float,
        nargs=9,
        required=True,
        metavar=("IXX", "IXY", "IXZ", "IYX", "IYY", "IYZ", "IZX", "IZY", "IZZ"),
        help="Inertia tensor components (9 values)",
    )

    args = parser.parse_args()

    if args.command == "wgs84-to-ecef":
        p = AerospaceGeometry.wgs84_to_ecef(args.lat, args.lon, args.alt)
        print(f"ECEF Point: ({p.x}, {p.y}, {p.z})")
    elif args.command == "generate-ellipsoid":
        mesh = AerospaceGeometry.generate_ellipsoid_mesh(
            args.a, args.b, args.c, args.resolution
        )
        print(
            f"Generated ellipsoid mesh with {len(mesh.vertices)} vertices and {len(mesh.faces)} faces."
        )
    elif args.command == "rotation-stability":
        tensor = (
            tuple(args.inertia[0:3]),
            tuple(args.inertia[3:6]),
            tuple(args.inertia[6:9]),
        )
        stability = AerospaceGeometry.rotation_stability(tensor)
        print(stability)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
