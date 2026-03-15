"""Acoustic Room Treatment and Ray Tracing algorithms."""

import argparse
import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class AcousticRaytracing:
    """Provides algorithms for simulating sound propagation in enclosed spaces."""

    @staticmethod
    def reflect_ray(
        incident: Tuple[float, float, float], normal: Tuple[float, float, float]
    ) -> Tuple[float, float, float]:
        """
        Calculates the specular reflection vector of an incident ray bouncing off a surface.
        r = d - 2(d.n)n
        """
        dot = (
            incident[0] * normal[0] + incident[1] * normal[1] + incident[2] * normal[2]
        )
        rx = incident[0] - 2 * dot * normal[0]
        ry = incident[1] - 2 * dot * normal[1]
        rz = incident[2] - 2 * dot * normal[2]

        mag = math.sqrt(rx * rx + ry * ry + rz * rz)
        if mag == 0:
            return (0, 0, 0)
        return (rx / mag, ry / mag, rz / mag)

    @staticmethod
    def estimate_rt60(
        volume: float, surface_area: float, avg_absorption_coeff: float
    ) -> float:
        """
        Estimates the Reverberation Time (RT60) using Sabine's formula.
        volume: Room volume in cubic meters.
        surface_area: Total room surface area in square meters.
        avg_absorption_coeff: Average absorption coefficient (0.0 to 1.0).
        Returns time in seconds for sound to decay by 60 dB.
        """
        if surface_area * avg_absorption_coeff == 0:
            return float("inf")
        return 0.161 * volume / (surface_area * avg_absorption_coeff)

    @staticmethod
    def fibonacci_sphere(samples: int = 100) -> List[Tuple[float, float, float]]:
        """Generates uniformly distributed points on a unit sphere."""
        points = []
        phi = math.pi * (3.0 - math.sqrt(5.0))  # golden angle in radians

        for i in range(samples):
            y = 1 - (i / float(samples - 1)) * 2  # y goes from 1 to -1
            radius = math.sqrt(1 - y * y)  # radius at y

            theta = phi * i  # golden angle increment

            x = math.cos(theta) * radius
            z = math.sin(theta) * radius
            points.append((x, y, z))

        return points


def main():
    parser = argparse.ArgumentParser(
        description="Acoustic Raytracing and Room Analysis Utilities"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # RT60 Tool
    rt60_parser = subparsers.add_parser("rt60", help="Estimate Reverberation Time (RT60)")
    rt60_parser.add_argument("--volume", type=float, required=True, help="Room volume in m^3")
    rt60_parser.add_argument("--area", type=float, required=True, help="Total surface area in m^2")
    rt60_parser.add_argument(
        "--absorption",
        type=float,
        required=True,
        help="Average absorption coefficient (0.0 to 1.0)",
    )

    # Reflect Tool
    reflect_parser = subparsers.add_parser("reflect", help="Calculate specular reflection")
    reflect_parser.add_argument(
        "--incident",
        type=float,
        nargs=3,
        required=True,
        metavar=("X", "Y", "Z"),
        help="Incident ray direction",
    )
    reflect_parser.add_argument(
        "--normal",
        type=float,
        nargs=3,
        required=True,
        metavar=("X", "Y", "Z"),
        help="Surface normal",
    )

    # Fibonacci Tool
    fib_parser = subparsers.add_parser("samples", help="Generate Fibonacci sphere samples")
    fib_parser.add_argument(
        "--count", type=int, default=100, help="Number of samples (default: 100)"
    )

    args = parser.parse_args()

    if args.command == "rt60":
        rt60 = AcousticRaytracing.estimate_rt60(args.volume, args.area, args.absorption)
        print(f"Estimated RT60: {rt60:.3f} seconds")
    elif args.command == "reflect":
        reflected = AcousticRaytracing.reflect_ray(tuple(args.incident), tuple(args.normal))
        print(f"Reflected Ray: ({reflected[0]:.4f}, {reflected[1]:.4f}, {reflected[2]:.4f})")
    elif args.command == "samples":
        points = AcousticRaytracing.fibonacci_sphere(args.count)
        print(f"Generated {len(points)} points on a unit sphere:")
        for p in points:
            print(f"{p[0]:.4f}, {p[1]:.4f}, {p[2]:.4f}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
