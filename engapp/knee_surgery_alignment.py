"""Total Knee Arthroplasty (TKA) alignment and surgical planning algorithms."""

import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


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
        distal_femur: TriangleMesh, resection_plane: Tuple[float, float, float, float]
    ) -> float:
        """
        Estimates the 'Gap' or thickness of bone to be removed.
        Measures the distance from the furthest distal point of the mesh to the resection plane.
        """
        nx, ny, nz, d = resection_plane
        max_dist = -float("inf")

        verts = (
            distal_femur.vertices()
            if hasattr(distal_femur, "vertices")
            else getattr(distal_femur, "_vertices", [])
        )
        for v in verts:
            # Signed distance to plane: (ax + by + cz + d) / sqrt(a^2 + b^2 + c^2)
            # Normal is already unit length
            dist = nx * v.x + ny * v.y + nz * getattr(v, "z", 0.0) + d
            if dist > max_dist:
                max_dist = dist

        return max_dist


def main():
    print("--- knee_surgery_alignment.py Demo ---")

    # 1. Coordinate Setup (in mm)
    hip = Point3D(0, 0, 450)  # Femoral head center
    knee = Point3D(0, 0, 0)  # Knee center (origin)

    # 2. Axis Calculation
    fma = KneeSurgeryAlignment.calculate_mechanical_axis(hip, knee)
    print(f"Mechanical Axis Vector: ({fma[0]:.3f}, {fma[1]:.3f}, {fma[2]:.3f})")

    # 3. Resection Planning
    # Standard distal cut is ~5-7 degrees valgus
    plane = KneeSurgeryAlignment.define_resection_plane(knee, fma, valgus_angle_deg=6.0)
    print(
        f"Planned Resection Plane: {plane[0]:.3f}x + {plane[1]:.3f}y + {plane[2]:.3f}z + {plane[3]:.1f} = 0"
    )

    # 4. Bone Removal Estimate
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def vertices(self):
            # Points on the distal condyles (lowest part of femur)
            return [MockPoint(20, 0, -5), MockPoint(-20, 0, -5)]

    femur = MockMesh()
    gap = KneeSurgeryAlignment.gap_analysis(femur, plane)
    print(f"Estimated Bone Resection Thickness: {abs(gap):.2f} mm")

    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
