"""Deployable Space Structures and Foldable Solar Panels."""

import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class DeployableStructures:
    """Provides algorithms for origami-inspired foldable structures (e.g., Miura-ori)."""

    @staticmethod
    def miura_ori_vertices(
        u_max: int, v_max: int, L: float, W: float, fold_angle_deg: float
    ) -> List[Point3D]:
        """
        Generates the vertices for a Miura-ori fold pattern based on the fold angle.
        u_max, v_max: Number of unit cells in the u and v directions.
        L, W: Length and width of a single parallelogram panel.
        fold_angle_deg: Angle of the fold (0 = fully flat, 90 = fully folded/packed).
        Returns a list of 3D points.
        """
        # Theta is the fold angle. 0 is flat open. 90 is tightly packed.
        theta = math.radians(fold_angle_deg)

        # Design angle of the parallelogram (gamma). Usually close to 45 or 60 degrees.
        gamma = math.radians(60.0)

        # The Miura-ori pattern compresses in both X and Y directions simultaneously
        # when the fold angle theta increases.
        # Equations derived from standard rigid origami kinematics.

        # H is the height of the folded structure
        H = L * math.sin(theta) * math.sin(gamma)

        # S_v is the projected length of L in the X direction
        S_v = L * math.cos(theta)

        # S_u is the projected length of W in the Y direction
        # This requires solving the spherical trigonometry of the degree-4 vertex.
        cos_xi = math.cos(gamma) * math.cos(gamma) + math.sin(gamma) * math.sin(
            gamma
        ) * math.cos(theta)
        # Prevent math domain error
        cos_xi = max(-1.0, min(1.0, cos_xi))
        xi = math.acos(cos_xi)

        S_u = W * math.cos(xi / 2.0)

        vertices = []
        for i in range(u_max + 1):
            for j in range(v_max + 1):
                # Zig-zag pattern
                zig_zag = ((-1) ** (i + j)) * H

                # In a real Miura fold, the vertices shift slightly in X/Y based on the angle
                # Simplified projection for visualization:
                x = j * S_v
                y = i * S_u + (j % 2) * (W * math.sin(gamma) * math.cos(theta))
                z = zig_zag if (i % 2 == 0) else -zig_zag

                vertices.append(Point3D(x, y, z))

        return vertices

    @staticmethod
    def calculate_packing_ratio(
        u_max: int, v_max: int, L: float, W: float, fold_angle_deg: float
    ) -> Tuple[float, float, float]:
        """
        Calculates the packing efficiency of the deployable panel.
        Returns (Deployed Area, Packed Projected Area, Packing Ratio).
        """
        # Deployed Area (when flat, fold_angle = 0)
        single_panel_area = (
            L * W * math.sin(math.radians(60.0))
        )  # Area of parallelogram
        total_deployed_area = (
            u_max * v_max * 2
        ) * single_panel_area  # 2 triangles per quad cell

        # Packed Projected Area (XY plane bounding box)
        pts = DeployableStructures.miura_ori_vertices(
            u_max, v_max, L, W, fold_angle_deg
        )
        x_coords = [p.x for p in pts]
        y_coords = [p.y for p in pts]

        if not x_coords:
            return 0.0, 0.0, 0.0

        packed_area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))

        if packed_area == 0:
            ratio = float(
                "inf"
            )  # Perfect packing (impossible in reality due to material thickness)
        else:
            ratio = total_deployed_area / packed_area

        return total_deployed_area, packed_area, ratio


def main():
    print("--- deployable_structures.py Demo ---")

    # 1. Define Panel specifications
    grid_u = 5  # 5 cells wide
    grid_v = 10  # 10 cells long
    L = 1.0  # meters
    W = 1.0  # meters

    print(f"Panel Grid: {grid_u} x {grid_v} cells (L={L}m, W={W}m)")

    # 2. Analyze different deployment states
    angles = [0.0, 45.0, 85.0]  # Flat, half-folded, tightly packed

    for angle in angles:
        print(f"\n--- State: {angle} degrees folded ---")
        pts = DeployableStructures.miura_ori_vertices(grid_u, grid_v, L, W, angle)

        # Calculate bounding box height to see how "thick" the folded stack is
        z_coords = [getattr(p, "z", 0.0) for p in pts]
        thickness = max(z_coords) - min(z_coords)

        dep_area, pack_area, ratio = DeployableStructures.calculate_packing_ratio(
            grid_u, grid_v, L, W, angle
        )

        print(f"Total Deployed Surface Area: {dep_area:.2f} m^2")
        print(f"Stowed/Projected Footprint: {pack_area:.2f} m^2")
        print(f"Stack Thickness (Z-height): {thickness:.2f} m")
        print(f"Packing Ratio (Deployed Area / Packed Area): {ratio:.2f}x")

    print("\nDemo completed successfully.")


if __name__ == "__main__":
    main()
