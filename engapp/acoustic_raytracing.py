"""Acoustic Room Treatment and Ray Tracing algorithms."""

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
    print("--- acoustic_raytracing.py Demo ---")

    # RT60 Estimation
    room_vol = 200.0  # m^3
    room_area = 210.0  # m^2
    absorption = 0.15  # typical for concrete/drywall

    rt60 = AcousticRaytracing.estimate_rt60(room_vol, room_area, absorption)
    print(f"Room Volume: {room_vol} m^3, Surface Area: {room_area} m^2")
    print(f"Average Absorption: {absorption}")
    print(f"Estimated RT60 (Reverberation Time): {rt60:.2f} seconds")

    # Ray reflection
    incident = (0.707, -0.707, 0.0)  # coming in at 45 degrees
    normal = (0.0, 1.0, 0.0)  # wall facing +Y
    reflected = AcousticRaytracing.reflect_ray(incident, normal)
    print(f"\nIncident Ray: {incident}")
    print(f"Wall Normal: {normal}")
    print(
        f"Reflected Ray: ({reflected[0]:.3f}, {reflected[1]:.3f}, {reflected[2]:.3f})"
    )
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
