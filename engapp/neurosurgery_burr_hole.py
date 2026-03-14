"""Neurosurgery Burr Hole planning and trajectory analysis."""

import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class BurrHolePlanning:
    """Provides algorithms for neurosurgical entry point and trajectory planning."""

    @staticmethod
    def entry_point_normal(
        mesh: TriangleMesh, point_idx: int
    ) -> Tuple[float, float, float]:
        """
        Calculates the surface normal at a specific vertex index.
        Used to ensure the burr drill is perpendicular to the skull.
        """
        # In a real TriangleMesh, we would average the normals of all adjacent faces.
        # Here we mock the behavior by finding faces containing the vertex.
        verts = (
            mesh.vertices()
            if hasattr(mesh, "vertices")
            else getattr(mesh, "_vertices", [])
        )
        faces = mesh.faces() if hasattr(mesh, "faces") else getattr(mesh, "_faces", [])

        adjacent_faces = [f for f in faces if point_idx in f]
        if not adjacent_faces:
            return (0, 0, 1)

        nx, ny, nz = 0.0, 0.0, 0.0
        for f in adjacent_faces:
            v0, v1, v2 = [verts[idx] for idx in f]
            # Cross product (v1-v0) x (v2-v0)
            ax, ay, az = (
                v1.x - v0.x,
                v1.y - v0.y,
                getattr(v1, "z", 0.0) - getattr(v0, "z", 0.0),
            )
            bx, by, bz = (
                v2.x - v0.x,
                v2.y - v0.y,
                getattr(v2, "z", 0.0) - getattr(v0, "z", 0.0),
            )

            fnx = ay * bz - az * by
            fny = az * bx - ax * bz
            fnz = ax * by - ay * bx

            mag = math.sqrt(fnx**2 + fny**2 + fnz**2)
            if mag > 0:
                nx += fnx / mag
                ny += fny / mag
                nz += fnz / mag

        total_mag = math.sqrt(nx**2 + ny**2 + nz**2)
        if total_mag == 0:
            return (0, 0, 1)
        return (nx / total_mag, ny / total_mag, nz / total_mag)

    @staticmethod
    def validate_drill_angle(
        surface_normal: Tuple[float, float, float],
        drill_dir: Tuple[float, float, float],
        max_angle_deg: float = 15.0,
    ) -> bool:
        """
        Validates that the drill is sufficiently perpendicular to the surface.
        If the angle is too steep, the drill bit might 'skate' or slip on the skull.
        """
        # Dot product: cos(theta) = n . d
        # Vectors must be normalized
        n_mag = math.sqrt(sum(x**2 for x in surface_normal))
        d_mag = math.sqrt(sum(x**2 for x in drill_dir))

        if n_mag == 0 or d_mag == 0:
            return False

        dot = sum(surface_normal[i] * drill_dir[i] for i in range(3)) / (n_mag * d_mag)
        angle = math.acos(max(-1.0, min(1.0, abs(dot))))

        return math.degrees(angle) <= max_angle_deg

    @staticmethod
    def estimate_bone_volume(radius: float, skull_thickness: float) -> float:
        """
        Estimates the volume of bone removed by the burr hole.
        Modeled as a cylinder: V = pi * r^2 * h
        """
        return math.pi * (radius**2) * skull_thickness


def main():
    print("--- neurosurgery_burr_hole.py Demo ---")

    # 1. Mock Skull Mesh entry point
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def vertices(self):
            return [MockPoint(0, 0, 0), MockPoint(1, 0, 0.1), MockPoint(0, 1, 0.1)]

        def faces(self):
            return [(0, 1, 2)]

    skull = MockMesh()

    # 2. Surface Analysis
    normal = BurrHolePlanning.entry_point_normal(skull, 0)
    print(
        f"Calculated Surface Normal at entry: ({normal[0]:.3f}, {normal[1]:.3f}, {normal[2]:.3f})"
    )

    # 3. Drill Path Validation
    planned_dir = (0, 0, -1)  # Drilling straight down
    is_valid = BurrHolePlanning.validate_drill_angle(normal, planned_dir)
    print(f"Planned Drill Direction: {planned_dir}")
    print(f"Angle Validation (Max 15 deg): {'PASS' if is_valid else 'FAIL'}")

    # 4. Metric Estimation
    vol = BurrHolePlanning.estimate_bone_volume(radius=7.0, skull_thickness=6.5)
    print(f"Estimated Bone Removal Volume (14mm burr): {vol:.1f} mm^3")

    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
