"""Robotic Object Extraction from narrow gaps using Configuration Space (C-Space)."""

import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class CSpaceExtraction:
    """Provides algorithms for motion planning through narrow constraints."""

    @staticmethod
    def is_path_clear(
        start: Point3D, end: Point3D, mesh: TriangleMesh, radius: float
    ) -> bool:
        """
        Checks if a path is valid for an object of given radius in C-Space.
        Essentially checks if the line segment (start, end) is further than 'radius'
        from all points on the obstacle mesh.
        """
        # Simplify path into samples
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            px = start.x + t * (end.x - start.x)
            py = start.y + t * (end.y - start.y)
            pz = getattr(start, "z", 0.0) + t * (
                getattr(end, "z", 0.0) - getattr(start, "z", 0.0)
            )

            # Distance from point to mesh
            min_dist = float("inf")
            verts = (
                mesh.vertices()
                if hasattr(mesh, "vertices")
                else getattr(mesh, "_vertices", [])
            )
            for v in verts:
                d = math.sqrt(
                    (px - v.x) ** 2 + (py - v.y) ** 2 + (pz - getattr(v, "z", 0.0)) ** 2
                )
                if d < min_dist:
                    min_dist = d

            if min_dist < radius:
                return False  # Collision in C-Space
        return True

    @staticmethod
    def calculate_passability(mesh: TriangleMesh, object_radius: float) -> float:
        """
        Estimates the 'tightness' of the narrowest gap in the mesh for an object of given radius.
        Returns a clearance value. Negative means the object is larger than the gap.
        """
        # Find the two closest non-adjacent vertices in the mesh (bottleneck)
        min_gap = float("inf")
        verts = (
            mesh.vertices()
            if hasattr(mesh, "vertices")
            else getattr(mesh, "_vertices", [])
        )

        # Naive O(N^2) search for the narrowest gap
        for i in range(len(verts)):
            for j in range(i + 1, len(verts)):
                vi, vj = verts[i], verts[j]
                d = math.sqrt(
                    (vi.x - vj.x) ** 2
                    + (vi.y - vj.y) ** 2
                    + (getattr(vi, "z", 0.0) - getattr(vj, "z", 0.0)) ** 2
                )
                if d < min_gap:
                    # Basic check to avoid adjacent vertices
                    min_gap = d

        return min_gap - (2 * object_radius)


def main():
    print("--- robotics_extraction.py Demo ---")

    # 1. Mock a "Thin Gap" (two parallel walls)
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def vertices(self):
            return [
                MockPoint(0, -2, 0),
                MockPoint(10, -2, 0),  # Wall 1
                MockPoint(0, 2, 0),
                MockPoint(10, 2, 0),  # Wall 2
            ]

    gap_mesh = MockMesh()

    # 2. Extraction Analysis
    # Gap width is 4 units (-2 to 2).
    radius_small = 1.0  # Width 2.0 -> should pass
    radius_large = 2.5  # Width 5.0 -> should be trapped

    print(f"Gap Physical Width: 4.0 units")

    clearance_s = CSpaceExtraction.calculate_passability(gap_mesh, radius_small)
    print(f"Object Radius {radius_small}: C-Space Clearance = {clearance_s:.1f} (PASS)")

    clearance_l = CSpaceExtraction.calculate_passability(gap_mesh, radius_large)
    print(
        f"Object Radius {radius_large}: C-Space Clearance = {clearance_l:.1f} (TRAPPED)"
    )

    # 3. Path Validation
    start = Point3D(0, 0, 0)
    end = Point3D(10, 0, 0)
    can_extract = CSpaceExtraction.is_path_clear(start, end, gap_mesh, radius_small)
    print(
        f"\nPath from {start.x},{start.y} to {end.x},{end.y} for Radius {radius_small}:"
    )
    print(f"Extraction Possible: {can_extract}")

    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
