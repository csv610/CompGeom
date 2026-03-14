"""Vascular Stenting simulation and Metal-to-Artery Ratio (MAR) analysis."""

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


class VascularStenting:
    """Provides algorithms for stent deployment and vessel coverage analysis."""

    @staticmethod
    def radial_expansion(
        stent: TriangleMesh, initial_radius: float, target_radius: float
    ) -> TriangleMesh:
        """
        Simulates the radial expansion of a stent from a catheter to the vessel wall.
        Scales vertices in the XY plane while preserving Z-length.
        """
        scale_factor = target_radius / initial_radius
        expanded_vertices = []

        for v in stent.vertices:
            # Scale radially in XY
            expanded_vertices.append(
                Point3D(v.x * scale_factor, v.y * scale_factor, getattr(v, "z", 0.0))
            )

        return TriangleMesh(expanded_vertices, stent.faces)

    @staticmethod
    def calculate_mar(
        stent: TriangleMesh, vessel_radius: float, vessel_length: float
    ) -> float:
        """
        Calculates the Metal-to-Artery Ratio (MAR).
        The percentage of the inner vessel wall surface covered by stent struts.
        """
        # 1. Calculate total internal surface area of the vessel (cylinder)
        # Area = 2 * pi * r * h
        vessel_surface_area = 2 * math.pi * vessel_radius * vessel_length

        # 2. Calculate total surface area of the stent mesh
        # We'll sum the areas of all triangles in the mesh
        stent_surface_area = 0.0
        verts = stent.vertices
        for face in stent.faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            # Cross product area
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

            cx = ay * bz - az * by
            cy = az * bx - ax * bz
            cz = ax * by - ay * bx

            stent_surface_area += 0.5 * math.sqrt(cx * cx + cy * cy + cz * cz)

        # MAR = Stent Area / Vessel Area
        if vessel_surface_area == 0:
            return 0.0
        return (stent_surface_area / vessel_surface_area) * 100.0

    @staticmethod
    def map_to_centerline(
        stent: TriangleMesh, centerline: List[Point3D]
    ) -> TriangleMesh:
        """
        Deforms a straight cylindrical stent to follow a curved vessel centerline.
        Uses a simplified Parallel Transport Frame approach.
        """
        # This is a complex operation. In this educational version,
        # we demonstrate the principle of coordinate transformation.
        deformed_vertices = []

        # Assume centerline points are equally spaced along Z
        z_min = min(getattr(v, "z", 0.0) for v in stent.vertices)
        z_max = max(getattr(v, "z", 0.0) for v in stent.vertices)
        z_range = z_max - z_min if z_max > z_min else 1.0

        for v in stent.vertices:
            # 1. Find normalized Z position
            t = (getattr(v, "z", 0.0) - z_min) / z_range
            idx = int(t * (len(centerline) - 1))

            # 2. Get local centerline position and orientation (tangent)
            origin = centerline[idx]
            # Simple offset: mapping XY local to global XYZ
            # (In a real implementation, we would use T, N, B frames)
            new_x = origin.x + v.x
            new_y = origin.y + v.y
            new_z = getattr(origin, "z", 0.0)

            deformed_vertices.append(Point3D(new_x, new_y, new_z))

        return TriangleMesh(deformed_vertices, stent.faces)


def main():
    print("--- vascular_stenting.py Demo ---")

    # 1. Generate a basic stent (reusing logic from medical_device)
    # 8 cells around, 10 cells long, radius 2mm, length 20mm
    radius = 2.0
    length = 20.0
    vertices = []
    faces = []
    circ, long = 8, 10
    for i in range(long + 1):
        z = (i / long) * length
        for j in range(circ):
            angle = 2 * math.pi * j / circ
            vertices.append(
                Point3D(radius * math.cos(angle), radius * math.sin(angle), z)
            )
    for i in range(long):
        for j in range(circ):
            p1, p2 = i * circ + j, (i + 1) * circ + j
            p3 = (i + 1) * circ + (j + 1) % circ
            faces.append((p1, p2, p3))

    stent = TriangleMesh(vertices, faces)
    print(f"Compressed Stent Radius: {radius} mm")

    # 2. Expansion
    vessel_radius = 3.5
    expanded_stent = VascularStenting.radial_expansion(stent, radius, vessel_radius)
    print(f"Expanded to Vessel Radius: {vessel_radius} mm")

    # 3. MAR Analysis
    mar = VascularStenting.calculate_mar(expanded_stent, vessel_radius, length)
    print(f"Metal-to-Artery Ratio (MAR): {mar:.2f}%")

    # 4. Centerline Mapping
    path = [Point3D(math.sin(z / 5.0) * 5, math.cos(z / 5.0) * 5, z) for z in range(21)]
    curved_stent = VascularStenting.map_to_centerline(expanded_stent, path)
    print(f"Mapped stent to curved centerline with {len(path)} waypoints.")

    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
