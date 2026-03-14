"""Indoor WiFi Router Placement and Signal Coverage Optimization."""

import math
from typing import List, Tuple, Optional

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


class WifiOptimizer:
    """Provides algorithms for maximizing indoor wireless coverage."""

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
    def calculate_signal_strength(
        router_pos: Tuple[float, float, float],
        target_pos: Tuple[float, float, float],
        mesh: TriangleMesh,
        wall_loss_db: float = 3.0,
    ) -> float:
        """
        Estimates the signal strength (dBm) at a target position.
        Uses Free-Space Path Loss (FSPL) and wall attenuation.
        """
        dx = target_pos[0] - router_pos[0]
        dy = target_pos[1] - router_pos[1]
        dz = target_pos[2] - router_pos[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        if dist < 0.1:
            return -20.0  # Max strength near router

        # 1. Free Space Path Loss (Simplified)
        # P = P0 - 20*log10(dist)
        strength = -30.0 - 20.0 * math.log10(dist)

        # 2. Wall Attenuation
        # Count intersections along the line of sight
        ray_dir = (dx / dist, dy / dist, dz / dist)

        verts = mesh.vertices if hasattr(mesh, "vertices") else []
        faces = mesh.faces if hasattr(mesh, "faces") else []

        wall_count = 0
        for face in faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            v0t = (v0.x, v0.y, getattr(v0, "z", 0.0))
            v1t = (v1.x, v1.y, getattr(v1, "z", 0.0))
            v2t = (v2.x, v2.y, getattr(v2, "z", 0.0))

            t = WifiOptimizer._ray_triangle_intersect(
                router_pos, ray_dir, v0t, v1t, v2t
            )
            if 0 < t < dist:
                wall_count += 1

        strength -= wall_count * wall_loss_db
        return strength

    @staticmethod
    def find_optimal_placement(
        mesh: TriangleMesh,
        test_points: List[Tuple[float, float, float]],
        router_candidates: List[Tuple[float, float, float]],
    ) -> Tuple[Tuple[float, float, float], float]:
        """
        Iterates through candidate router locations to find the one that
        maximizes the average signal strength across all test points.
        """
        best_pos = (0, 0, 0)
        best_avg_strength = -float("inf")

        for router in router_candidates:
            total_strength = 0.0
            for target in test_points:
                total_strength += WifiOptimizer.calculate_signal_strength(
                    router, target, mesh
                )

            avg = total_strength / len(test_points)
            if avg > best_avg_strength:
                best_avg_strength = avg
                best_pos = router

        return best_pos, best_avg_strength


def main():
    print("--- wifi_placement_optimizer.py Demo ---")

    # 1. Mock a simple indoor environment (a 10x10 floor and a central wall)
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def __init__(self):
            # Wall at x=5, from y=0 to y=10
            self.vertices = [
                MockPoint(5, 0, 0),
                MockPoint(5, 10, 0),
                MockPoint(5, 5, 3),
            ]
            self.faces = [(0, 1, 2)]

    house_mesh = MockMesh()

    # 2. Define target test points (where we want good signal)
    # Sampling across the floor
    targets = []
    for x in [2, 8]:
        for y in [2, 8]:
            targets.append((x, y, 1.0))

    # 3. Define candidate router locations (corners and center)
    candidates = [(0, 0, 2), (5, 5, 2), (9, 9, 2)]

    print(f"Testing {len(candidates)} router locations across {len(targets)} rooms...")

    best_p, best_s = WifiOptimizer.find_optimal_placement(
        house_mesh, targets, candidates
    )

    print(f"\nOptimal Router Location: {best_p}")
    print(f"Average Signal Strength: {best_s:.2f} dBm")

    # Show dead zones
    print("\nIndividual coverage report for best location:")
    for t in targets:
        s = WifiOptimizer.calculate_signal_strength(best_p, t, house_mesh)
        status = "EXCELLENT" if s > -50 else "GOOD" if s > -70 else "POOR"
        print(f" - Point {t}: {s:.1f} dBm ({status})")

    print("\nDemo completed successfully.")


if __name__ == "__main__":
    main()
