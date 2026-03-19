"""Total Knee Arthroplasty (TKA) alignment and surgical planning algorithms."""

import math
import argparse
from typing import List, Tuple

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
except ImportError:

    class TriMesh:
        def __init__(self, vertices=None, faces=None):
            self.vertices = vertices or []
            self.faces = faces or []

    class Point3D:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x, self.y, self.z = x, y, z


class KneeSurgeryAlignment:
    """Provides algorithms for mechanical axis alignment and resection planning."""

    @staticmethod
    def calculate_mechanical_axis(
        femoral_head_center: Point3D, knee_center: Point3D
    ) -> Tuple[float, float, float]:
        """
        Calculates the Femoral Mechanical Axis (FMA).
        This is the primary reference for knee alignment.
        Returns a normalized direction vector.
        """
        dx = knee_center.x - femoral_head_center.x
        dy = knee_center.y - femoral_head_center.y
        dz = getattr(knee_center, "z", 0.0) - getattr(femoral_head_center, "z", 0.0)

        mag = math.sqrt(dx * dx + dy * dy + dz * dz)
        if mag == 0:
            return (0, 0, 1)
        return (dx / mag, dy / mag, dz / mag)

    @staticmethod
    def define_resection_plane(
        knee_center: Point3D,
        mechanical_axis: Tuple[float, float, float],
        valgus_angle_deg: float = 5.0,
    ) -> Tuple[float, float, float, float]:
        """
        Defines the Distal Femoral Resection Plane.
        The plane is typically tilted (valgus angle) relative to the mechanical axis.
        Returns plane coefficients (ax + by + cz + d = 0).
        """
        # For simplicity, we rotate the mechanical axis by the valgus angle around the anterior-posterior axis
        # In a real scenario, this involves a specific 3D rotation matrix.
        # Here we assume mechanical axis is roughly Z-aligned.

        rad = math.radians(valgus_angle_deg)
        # Assuming axis is (0,0,1), rotation around Y (valgus tilt)
        nx = math.sin(rad)
        ny = 0.0
        nz = math.cos(rad)

        # Point-normal form: nx(x - x0) + ny(y - y0) + nz(z - z0) = 0
        d = -(
            nx * knee_center.x
            + ny * knee_center.y
            + nz * getattr(knee_center, "z", 0.0)
        )

        return (nx, ny, nz, d)

    @staticmethod
    def gap_analysis(
        distal_femur: TriMesh, resection_plane: Tuple[float, float, float, float]
    ) -> float:
        """
        Estimates the 'Gap' or thickness of bone to be removed.
        Measures the distance from the furthest distal point of the mesh to the resection plane.
        """
        nx, ny, nz, d = resection_plane
        max_dist = -float("inf")

        if hasattr(distal_femur, "vertices") and callable(distal_femur.vertices):
            verts = distal_femur.vertices()
        elif hasattr(distal_femur, "vertices"):
            verts = distal_femur.vertices
        else:
            verts = getattr(distal_femur, "_vertices", [])

        for v in verts:
            # Signed distance to plane: (ax + by + cz + d) / sqrt(a^2 + b^2 + c^2)
            # Normal is already unit length
            dist = nx * v.x + ny * v.y + nz * getattr(v, "z", 0.0) + d
            if dist > max_dist:
                max_dist = dist

        return max_dist


def main():
    parser = argparse.ArgumentParser(description="Total Knee Arthroplasty (TKA) alignment and surgical planning algorithms.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # calculate_mechanical_axis
    axis_parser = subparsers.add_parser(
        "calculate_mechanical_axis",
        help="Calculates the Femoral Mechanical Axis (FMA).",
    )
    axis_parser.add_argument(
        "--hip",
        type=float,
        nargs=3,
        default=[0.0, 0.0, 450.0],
        help="Hip center coordinates (default: 0 0 450)",
    )
    axis_parser.add_argument(
        "--knee",
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0],
        help="Knee center coordinates (default: 0 0 0)",
    )

    # define_resection_plane
    plane_parser = subparsers.add_parser(
        "define_resection_plane",
        help="Defines the Distal Femoral Resection Plane.",
    )
    plane_parser.add_argument(
        "--knee",
        type=float,
        nargs=3,
        default=[0.0, 0.0, 0.0],
        help="Knee center coordinates (default: 0 0 0)",
    )
    plane_parser.add_argument(
        "--valgus_angle",
        type=float,
        default=5.0,
        help="Valgus angle in degrees (default: 5.0)",
    )

    # gap_analysis
    gap_parser = subparsers.add_parser(
        "gap_analysis",
        help="Estimates the 'Gap' or thickness of bone to be removed.",
    )

    args = parser.parse_args()

    # Shared setup
    hip_pt = Point3D(0, 0, 450)
    knee_pt = Point3D(0, 0, 0)
    tools = KneeSurgeryAlignment()

    # Mock Mesh for gap analysis
    class MockMesh:
        def vertices(self):
            return [Point3D(20, 0, -5), Point3D(-20, 0, -5)]
    femur = MockMesh()

    if args.command == "calculate_mechanical_axis":
        h = Point3D(*args.hip)
        k = Point3D(*args.knee)
        fma = tools.calculate_mechanical_axis(h, k)
        print(f"Mechanical Axis Vector: ({fma[0]:.3f}, {fma[1]:.3f}, {fma[2]:.3f})")
    elif args.command == "define_resection_plane":
        k = Point3D(*args.knee)
        fma = (0, 0, 1) # dummy axis for independent call
        plane = tools.define_resection_plane(k, fma, args.valgus_angle)
        print(f"Planned Resection Plane: {plane[0]:.3f}x + {plane[1]:.3f}y + {plane[2]:.3f}z + {plane[3]:.1f} = 0")
    elif args.command == "gap_analysis":
        # Needs a plane
        plane = (0.087, 0.0, 0.996, 0.0) # approx 5 deg valgus at origin
        gap = tools.gap_analysis(femur, plane)
        print(f"Estimated Bone Resection Thickness: {abs(gap):.2f} mm")
    else:
        # Default behavior: run demo
        print("--- knee_surgery_alignment.py Demo ---")
        fma = tools.calculate_mechanical_axis(hip_pt, knee_pt)
        print(f"Mechanical Axis Vector: ({fma[0]:.3f}, {fma[1]:.3f}, {fma[2]:.3f})")
        plane = tools.define_resection_plane(knee_pt, fma, valgus_angle_deg=6.0)
        print(f"Planned Resection Plane: {plane[0]:.3f}x + {plane[1]:.3f}y + {plane[2]:.3f}z + {plane[3]:.1f} = 0")
        gap = tools.gap_analysis(femur, plane)
        print(f"Estimated Bone Resection Thickness: {abs(gap):.2f} mm")
        print("\nUse --help to see CLI options.")


if __name__ == "__main__":
    main()
