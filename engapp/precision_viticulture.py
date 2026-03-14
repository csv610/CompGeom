"""Precision Viticulture and Drone Flight Planning algorithms."""

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


class PrecisionViticulture:
    """Provides algorithms for vineyard terrain analysis and drone path planning."""

    @staticmethod
    def calculate_terrain_following_path(
        ground_mesh: TriangleMesh,
        survey_points: List[Tuple[float, float]],
        altitude: float,
    ) -> List[Point3D]:
        """
        Calculates a drone flight path that maintains a constant altitude above the terrain.
        survey_points: (x, y) coordinates of the planned 2D grid path.
        """
        flight_path = []

        verts = ground_mesh.vertices if hasattr(ground_mesh, "vertices") else []
        faces = ground_mesh.faces if hasattr(ground_mesh, "faces") else []

        for px, py in survey_points:
            # Find the triangle in the mesh that contains (px, py)
            # and interpolate its Z value (Barycentric Coordinates)
            ground_z = 0.0
            found = False

            for face in faces:
                v0, v1, v2 = [verts[idx] for idx in face]

                # 2D point-in-triangle check (projected on XY plane)
                def cross_product_2d(a, b, c):
                    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

                cp1 = cross_product_2d(v0, v1, Point3D(px, py, 0))
                cp2 = cross_product_2d(v1, v2, Point3D(px, py, 0))
                cp3 = cross_product_2d(v2, v0, Point3D(px, py, 0))

                if (cp1 >= 0 and cp2 >= 0 and cp3 >= 0) or (
                    cp1 <= 0 and cp2 <= 0 and cp3 <= 0
                ):
                    # Point is inside. Interpolate Z using barycentric coordinates
                    denom = (v1.y - v2.y) * (v0.x - v2.x) + (v2.x - v1.x) * (
                        v0.y - v2.y
                    )
                    if abs(denom) < 1e-9:
                        continue

                    w0 = (
                        (v1.y - v2.y) * (px - v2.x) + (v2.x - v1.x) * (py - v2.y)
                    ) / denom
                    w1 = (
                        (v2.y - v0.y) * (px - v2.x) + (v0.x - v2.x) * (py - v2.y)
                    ) / denom
                    w2 = 1.0 - w0 - w1

                    ground_z = (
                        w0 * getattr(v0, "z", 0.0)
                        + w1 * getattr(v1, "z", 0.0)
                        + w2 * getattr(v2, "z", 0.0)
                    )
                    found = True
                    break

            # If not found, use a baseline (average mesh Z or 0)
            if not found and verts:
                ground_z = sum(getattr(v, "z", 0.0) for v in verts) / len(verts)

            flight_path.append(Point3D(px, py, ground_z + altitude))

        return flight_path

    @staticmethod
    def camera_footprint_area(drone_pos: Point3D, fov_deg: float) -> float:
        """
        Calculates the 2D area (m^2) visible to the drone's multispectral camera.
        Assumes flat ground for simple estimation.
        """
        altitude = getattr(drone_pos, "z", 0.0)
        # FOV is total angle. Half-angle is fov/2.
        radius = altitude * math.tan(math.radians(fov_deg / 2.0))
        return math.pi * (radius**2)

    @staticmethod
    def estimate_vine_density(ground_mesh: TriangleMesh, mesh_area: float) -> float:
        """
        Estimates the potential vine count based on surface area and spacing.
        Vineyards on slopes have more surface area than their 2D footprint.
        """
        # Spacing: 1.5m between vines, 2.5m between rows
        spacing = 1.5 * 2.5
        return mesh_area / spacing


def main():
    print("--- precision_viticulture.py Demo ---")

    # 1. Mock a Sloped Vineyard Terrain
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def __init__(self):
            # A 100x100m plot with a 10m rise in Z
            self.vertices = [
                MockPoint(0, 0, 0),
                MockPoint(100, 0, 0),
                MockPoint(100, 100, 10),
                MockPoint(0, 100, 10),
            ]
            self.faces = [(0, 1, 2), (0, 2, 3)]

    vineyard = MockMesh()

    # 2. Path Planning (Maintain 30m altitude)
    points_2d = [(25, 25), (50, 50), (75, 75)]
    altitude = 30.0

    print(f"Generating terrain-following flight path at {altitude}m altitude...")
    path = PrecisionViticulture.calculate_terrain_following_path(
        vineyard, points_2d, altitude
    )

    for i, p in enumerate(path):
        print(f" - Waypoint {i}: ({p.x}, {p.y}, {p.z:.2f})")

    # 3. Camera Analysis
    fov = 60.0  # Wide angle camera
    area = PrecisionViticulture.camera_footprint_area(path[1], fov)
    print(f"\nCamera FOV: {fov} degrees")
    print(f"Ground Coverage Area at 30m: {area:.2f} m^2")

    print("\nDemo completed successfully.")


if __name__ == "__main__":
    main()
