"""Radiation Therapy Planning and Oncology geometry algorithms."""

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


class RadiationOncology:
    """Provides algorithms for calculating radiation beam paths and organ safety."""

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
        return t if t > eps else -1.0

    @staticmethod
    def calculate_tissue_depth(
        body_mesh: TriangleMesh, beam_source: Point3D, tumor_center: Point3D
    ) -> float:
        """
        Calculates how much tissue the radiation beam must pass through to reach the tumor.
        Essential for 'Dose Calculation' (radiation weakens as it goes deeper).
        """
        source = (beam_source.x, beam_source.y, getattr(beam_source, "z", 0.0))
        target = (tumor_center.x, tumor_center.y, getattr(tumor_center, "z", 0.0))

        dx, dy, dz = target[0] - source[0], target[1] - source[1], target[2] - source[2]
        dist_to_tumor = math.sqrt(dx * dx + dy * dy + dz * dz)
        ray_dir = (dx / dist_to_tumor, dy / dist_to_tumor, dz / dist_to_tumor)

        # Find the first intersection with the skin (body mesh)
        verts = body_mesh.vertices if hasattr(body_mesh, "vertices") else []
        faces = body_mesh.faces if hasattr(body_mesh, "faces") else []

        min_t = float("inf")
        for face in faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            t = RadiationOncology._ray_triangle_intersect(
                source,
                ray_dir,
                (v0.x, v0.y, getattr(v0, "z", 0.0)),
                (v1.x, v1.y, getattr(v1, "z", 0.0)),
                (v2.x, v2.y, getattr(v2, "z", 0.0)),
            )
            if 0 < t < min_t:
                min_t = t

        if min_t == float("inf"):
            return 0.0  # Missed the body entirely

        # Tissue depth is distance from skin to tumor center
        return dist_to_tumor - min_t

    @staticmethod
    def check_organ_collision(
        oar_mesh: TriangleMesh, beam_source: Point3D, tumor_center: Point3D
    ) -> bool:
        """
        Checks if a radiation beam passes through an Organ-at-Risk (OAR).
        OARs (like the spinal cord) must be avoided to prevent paralysis.
        """
        source = (beam_source.x, beam_source.y, getattr(beam_source, "z", 0.0))
        target = (tumor_center.x, tumor_center.y, getattr(tumor_center, "z", 0.0))

        dx, dy, dz = target[0] - source[0], target[1] - source[1], target[2] - source[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        ray_dir = (dx / dist, dy / dist, dz / dist)

        verts = oar_mesh.vertices if hasattr(oar_mesh, "vertices") else []
        faces = oar_mesh.faces if hasattr(oar_mesh, "faces") else []

        for face in faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            t = RadiationOncology._ray_triangle_intersect(
                source,
                ray_dir,
                (v0.x, v0.y, getattr(v0, "z", 0.0)),
                (v1.x, v1.y, getattr(v1, "z", 0.0)),
                (v2.x, v2.y, getattr(v2, "z", 0.0)),
            )
            if 0 < t < dist:
                return True  # Beam hits the critical organ!
        return False


def main():
    print("--- radiation_oncology.py Demo ---")

    # 1. Mock Anatomy
    # Tumor is at the center
    tumor = Point3D(0, 0, 0)

    # Mock Body Skin (a large triangle in front of tumor)
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def __init__(self, verts, faces):
            self.vertices = verts
            self.faces = faces

    # Skin at x = -50mm
    skin_mesh = MockMesh(
        [MockPoint(-50, -100, -100), MockPoint(-50, 100, -100), MockPoint(-50, 0, 100)],
        [(0, 1, 2)],
    )

    # Spine (Organ-at-Risk) at x = 20mm (behind tumor)
    spine_mesh = MockMesh(
        [MockPoint(20, -10, -10), MockPoint(20, 10, -10), MockPoint(20, 0, 10)],
        [(0, 1, 2)],
    )

    # 2. Test Beam Angles
    # Beam A: Frontal (Safe)
    source_a = Point3D(-100, 0, 0)
    # Beam B: Oblique (Hits Spine)
    source_b = Point3D(100, 0, 0)

    for i, source in enumerate([source_a, source_b]):
        name = "A (Frontal)" if i == 0 else "B (Back/Oblique)"
        print(f"\nAnalyzing Beam {name}:")

        depth = RadiationOncology.calculate_tissue_depth(skin_mesh, source, tumor)
        hit_oar = RadiationOncology.check_organ_collision(spine_mesh, source, tumor)

        print(f" - Tissue Depth to Tumor: {depth:.1f} mm")
        print(f" - Hits Spinal Cord: {'YES (DANGEROUS)' if hit_oar else 'NO (SAFE)'}")

    print("\nDemo completed successfully.")


if __name__ == "__main__":
    main()
