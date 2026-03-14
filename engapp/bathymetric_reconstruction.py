"""Marine Archaeology and Bathymetric Reconstruction algorithms."""

import math
from typing import List, Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriangleMesh = object
    Point3D = object


class BathymetricReconstruction:
    """Provides algorithms for reconstructing surfaces from sonar point clouds."""

    @staticmethod
    def generate_sdf_grid(
        points: List[Point3D],
        grid_size: int,
        bmin: Tuple[float, float, float],
        bmax: Tuple[float, float, float],
    ) -> List[List[List[float]]]:
        """
        Generates a Signed Distance Function (SDF) grid from a point cloud.
        Uses a naive O(N*M) approach where N is grid cells and M is points.
        (For production, a KD-Tree should be used).
        """
        pts = [(p.x, p.y, getattr(p, "z", 0.0)) for p in points]

        dx = (bmax[0] - bmin[0]) / grid_size
        dy = (bmax[1] - bmin[1]) / grid_size
        dz = (bmax[2] - bmin[2]) / grid_size

        grid = []
        for i in range(grid_size):
            plane = []
            x = bmin[0] + i * dx
            for j in range(grid_size):
                row = []
                y = bmin[1] + j * dy
                for k in range(grid_size):
                    z = bmin[2] + k * dz

                    # Find distance to nearest point
                    min_d2 = float("inf")
                    for px, py, pz in pts:
                        d2 = (x - px) ** 2 + (y - py) ** 2 + (z - pz) ** 2
                        if d2 < min_d2:
                            min_d2 = d2

                    # True SDF needs 'inside/outside' signs.
                    # For a simple thickness reconstruction around points, we offset by a radius
                    radius = (dx + dy + dz) / 3.0  # blob thickness
                    sdf_val = math.sqrt(min_d2) - radius
                    row.append(sdf_val)
                plane.append(row)
            grid.append(plane)

        return grid

    @staticmethod
    def estimate_displaced_volume(mesh: TriangleMesh) -> float:
        """
        Estimates the volume of the reconstructed mesh to guess ship weight.
        Uses the divergence theorem (sum of signed tetrahedron volumes).
        """
        try:
            from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis

            return MeshAnalysis.total_volume(mesh)
        except ImportError:
            # Fallback calculation if library missing
            vol = 0.0
            verts = (
                mesh.vertices()
                if hasattr(mesh, "vertices")
                else getattr(mesh, "_vertices", [])
            )
            faces = (
                mesh.faces() if hasattr(mesh, "faces") else getattr(mesh, "_faces", [])
            )

            for face in faces:
                v0, v1, v2 = [verts[idx] for idx in face]
                v0t = (v0.x, v0.y, getattr(v0, "z", 0.0))
                v1t = (v1.x, v1.y, getattr(v1, "z", 0.0))
                v2t = (v2.x, v2.y, getattr(v2, "z", 0.0))

                # Signed volume of tetrahedron from origin
                v = (
                    v0t[0] * v1t[1] * v2t[2]
                    - v0t[0] * v2t[1] * v1t[2]
                    - v1t[0] * v0t[1] * v2t[2]
                    + v1t[0] * v2t[1] * v0t[2]
                    + v2t[0] * v0t[1] * v1t[2]
                    - v2t[0] * v1t[1] * v0t[2]
                ) / 6.0
                vol += v
            return abs(vol)


def main():
    print("--- bathymetric_reconstruction.py Demo ---")

    # Mock some sonar pings along a line
    class MockPoint:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    sonar_pings = [MockPoint(x, 0, 0) for x in range(5)]
    print(f"Generated {len(sonar_pings)} sonar ping points.")

    bmin = (-2, -2, -2)
    bmax = (6, 2, 2)
    grid_size = 5

    print(
        f"Computing SDF grid ({grid_size}x{grid_size}x{grid_size}) (Naïve approach)..."
    )
    grid = BathymetricReconstruction.generate_sdf_grid(
        sonar_pings, grid_size, bmin, bmax
    )

    # Just show a sample from the grid
    sample_val = grid[2][2][2]
    print(f"SDF Sample value near origin: {sample_val:.3f}")

    print("Normally, Marching Cubes would extract a TriangleMesh from this grid.")
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
