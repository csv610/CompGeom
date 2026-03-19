"""Flood Risk Analysis and Disaster Mitigation algorithms."""

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
            self.x = x
            self.y = y
            self.z = z


class FloodRiskAnalysis:
    """Provides algorithms for analyzing flood zones and submerged volumes."""

    @staticmethod
    def identify_submerged_faces(mesh: TriMesh, water_level: float) -> List[int]:
        """
        Identifies triangles in the mesh that are completely or partially submerged.
        Useful for generating hazard maps for urban planners.
        """
        submerged_indices = []
        verts = mesh.vertices if hasattr(mesh, "vertices") else []
        faces = mesh.faces if hasattr(mesh, "faces") else []

        for i, face in enumerate(faces):
            # If any vertex of the triangle is below water_level, it is at risk
            is_submerged = False
            for idx in face:
                if getattr(verts[idx], "z", 0.0) <= water_level:
                    is_submerged = True
                    break
            if is_submerged:
                submerged_indices.append(i)

        return submerged_indices

    @staticmethod
    def calculate_flood_volume(mesh: TriMesh, water_level: float) -> float:
        """
        Calculates the total volume of water accumulated over the terrain up to water_level.
        V = Sum(Area_i * (WaterLevel - AvgHeight_i)) for all submerged parts.
        """
        total_vol = 0.0
        verts = mesh.vertices if hasattr(mesh, "vertices") else []
        faces = mesh.faces if hasattr(mesh, "faces") else []

        for face in faces:
            v0, v1, v2 = [verts[idx] for idx in face]
            v0t = (v0.x, v0.y, getattr(v0, "z", 0.0))
            v1t = (v1.x, v1.y, getattr(v1, "z", 0.0))
            v2t = (v2.x, v2.y, getattr(v2, "z", 0.0))

            # Average height of the triangle
            avg_z = (v0t[2] + v1t[2] + v2t[2]) / 3.0

            if avg_z < water_level:
                # 2D Area of triangle (projected on XY plane)
                area_2d = 0.5 * abs(
                    v0t[0] * (v1t[1] - v2t[1])
                    + v1t[0] * (v2t[1] - v0t[1])
                    + v2t[0] * (v0t[1] - v1t[1])
                )
                # Volume of water 'column' above this triangle
                total_vol += area_2d * (water_level - avg_z)

        return total_vol


def main():
    parser = argparse.ArgumentParser(description="Flood Risk Analysis and Disaster Mitigation algorithms.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # identify_submerged_faces
    submerged_parser = subparsers.add_parser(
        "identify_submerged_faces",
        help="Identifies triangles in the mesh that are completely or partially submerged.",
    )
    submerged_parser.add_argument(
        "--water_level",
        type=float,
        default=5.0,
        help="Water level for analysis (default: 5.0)",
    )

    # calculate_flood_volume
    volume_parser = subparsers.add_parser(
        "calculate_flood_volume",
        help="Calculates the total volume of water accumulated over the terrain up to water_level.",
    )
    volume_parser.add_argument(
        "--water_level",
        type=float,
        default=5.0,
        help="Water level for analysis (default: 5.0)",
    )

    args = parser.parse_args()

    # Mock Terrain (a valley)
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class MockMesh:
        def __init__(self):
            self.vertices = [
                MockPoint(0, 0, 10),
                MockPoint(100, 0, 10),  # High edges
                MockPoint(50, 50, 0),
                MockPoint(50, -50, 0),  # Low center (valley)
            ]
            self.faces = [(0, 1, 2), (0, 1, 3)]

    terrain = MockMesh()
    tools = FloodRiskAnalysis()

    if args.command == "identify_submerged_faces":
        submerged = tools.identify_submerged_faces(terrain, args.water_level)
        print(f"Submerged faces at level {args.water_level}: {submerged}")
    elif args.command == "calculate_flood_volume":
        volume = tools.calculate_flood_volume(terrain, args.water_level)
        print(f"Estimated water volume at level {args.water_level}: {volume:,.1f} m^3")
    else:
        # Default behavior: run demo
        print("--- flood_risk_analysis.py Demo ---")
        levels = [2.0, 5.0, 12.0]
        for level in levels:
            print(f"\n--- Flood Level: {level} meters ---")
            submerged = tools.identify_submerged_faces(terrain, level)
            volume = tools.calculate_flood_volume(terrain, level)
            print(f" - Risk: {len(submerged)} of {len(terrain.faces)} triangles submerged.")
            print(f" - Estimated Water Volume: {volume:,.1f} m^3")
            if level > 10.0:
                print(" - Status: CRITICAL (Valley overflowing)")
            else:
                print(" - Status: CONTAINED (Water within valley)")
        print("\nUse --help to see CLI options.")


if __name__ == "__main__":
    main()
