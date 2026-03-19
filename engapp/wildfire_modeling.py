"""Wildfire Spread Simulation based on terrain geometry."""

import argparse
import math
from typing import Tuple

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriMesh = object
    Point3D = object


class WildfireModeling:
    """Provides algorithms for calculating fire spread across a topographical mesh."""

    @staticmethod
    def calculate_slope_and_aspect(
        normal: Tuple[float, float, float],
    ) -> Tuple[float, float]:
        """
        Calculates the slope (steepness) and aspect (direction) of a terrain face.
        normal: The face normal vector (x, y, z). Up is (0, 0, 1).
        Returns slope in radians, aspect in radians (from North, clockwise).
        """
        nx, ny, nz = normal
        # Normal vector must point up
        if nz < 0:
            nx, ny, nz = -nx, -ny, -nz

        mag = math.sqrt(nx * nx + ny * ny + nz * nz)
        if mag == 0:
            return 0.0, 0.0

        nx, ny, nz = nx / mag, ny / mag, nz / mag

        # Slope is angle between normal and vertical (0,0,1)
        # Using clamp to avoid domain errors due to floating point precision
        slope = math.acos(max(-1.0, min(1.0, nz)))

        # Aspect is direction of steepest descent (projection of normal on XY plane)
        # Assuming Y is North, X is East.
        aspect = math.atan2(nx, ny)
        if aspect < 0:
            aspect += 2 * math.pi

        return slope, aspect

    @staticmethod
    def rate_of_spread(
        base_ros: float,
        wind_vector: Tuple[float, float, float],
        normal: Tuple[float, float, float],
    ) -> float:
        """
        Calculates the Rate of Spread (ROS) for a fire moving across a face.
        Combines base spread, wind effect, and slope effect.
        """
        slope, aspect = WildfireModeling.calculate_slope_and_aspect(normal)

        wx, wy, wz = wind_vector
        wind_mag = math.sqrt(wx * wx + wy * wy + wz * wz)

        # Simple empirical model: ROS = base * (1 + wind_factor) * (1 + slope_factor)
        # Wind factor: dot product of wind and uphill direction (fire travels faster uphill and with wind)

        # Project wind onto the face plane
        dot_wind_norm = wx * normal[0] + wy * normal[1] + wz * normal[2]
        wind_proj = (
            wx - dot_wind_norm * normal[0],
            wy - dot_wind_norm * normal[1],
            wz - dot_wind_norm * normal[2],
        )

        proj_mag = math.sqrt(wind_proj[0] ** 2 + wind_proj[1] ** 2 + wind_proj[2] ** 2)

        # Uphill direction on the face
        uphill_dir = (0, 0, 1)
        dot_up_norm = uphill_dir[2] * normal[2]
        up_proj = (
            -dot_up_norm * normal[0],
            -dot_up_norm * normal[1],
            1 - dot_up_norm * normal[2],
        )
        up_mag = math.sqrt(up_proj[0] ** 2 + up_proj[1] ** 2 + up_proj[2] ** 2)

        wind_factor = 0.0
        if proj_mag > 0 and up_mag > 0:
            # How aligned is wind with uphill?
            alignment = (
                wind_proj[0] * up_proj[0]
                + wind_proj[1] * up_proj[1]
                + wind_proj[2] * up_proj[2]
            ) / (proj_mag * up_mag)
            wind_factor = (
                wind_mag * max(0, alignment) * 0.1
            )  # Arbitrary scaling coefficient

        # Slope factor (exponential increase with slope)
        slope_deg = math.degrees(slope)
        slope_factor = (
            math.exp(0.069 * slope_deg) - 1.0
        )  # Standard Rothermel approximation shape

        return base_ros * (1.0 + wind_factor) * (1.0 + slope_factor)


def main():
    parser = argparse.ArgumentParser(
        description="Wildfire Spread Simulation based on terrain geometry."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # Slope/Aspect Tool
    topo_parser = subparsers.add_parser("topo", help="Calculate slope and aspect from normal")
    topo_parser.add_argument("--normal", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Face normal vector")

    # ROS Tool
    ros_parser = subparsers.add_parser("ros", help="Calculate Rate of Spread (ROS)")
    ros_parser.add_argument("--base", type=float, default=1.0, help="Base rate of spread (m/min)")
    ros_parser.add_argument("--wind", type=float, nargs=3, default=[0, 10, 0], metavar=("X", "Y", "Z"), help="Wind vector")
    ros_parser.add_argument("--normal", type=float, nargs=3, required=True, metavar=("X", "Y", "Z"), help="Face normal vector")

    args = parser.parse_args()

    if args.command == "topo":
        slope, aspect = WildfireModeling.calculate_slope_and_aspect(tuple(args.normal))
        print(f"Face Slope: {math.degrees(slope):.1f} degrees")
        print(f"Face Aspect: {math.degrees(aspect):.1f} degrees (0=N, 90=E)")
    elif args.command == "ros":
        ros = WildfireModeling.rate_of_spread(args.base, tuple(args.wind), tuple(args.normal))
        print(f"Effective ROS: {ros:.2f} m/min")
    else:
        # Default demo behavior
        print("--- wildfire_modeling.py Demo ---")
        normal = (0.0, -0.5, 0.866)
        slope, aspect = WildfireModeling.calculate_slope_and_aspect(normal)
        print(f"Face Slope: {math.degrees(slope):.1f} degrees")
        print(f"Face Aspect: {math.degrees(aspect):.1f} degrees (0=N, 90=E)")
        print("Demo completed successfully. Use -h for CLI options.")


if __name__ == "__main__":
    main()
