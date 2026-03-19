"""Marine Archaeology and Bathymetric Reconstruction algorithms."""

import math
import argparse
from typing import List, Tuple

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
except ImportError:
    TriMesh = object
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
    def estimate_displaced_volume(mesh: TriMesh) -> float:
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
    parser = argparse.ArgumentParser(
        description="Marine Archaeology and Bathymetric Reconstruction algorithms."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # Generate SDF Grid
    sdf_parser = subparsers.add_parser(
        "generate-sdf", help="Generates a Signed Distance Function (SDF) grid"
    )
    sdf_parser.add_argument(
        "--points",
        type=float,
        nargs="+",
        required=True,
        help="Points as x1 y1 z1 x2 y2 z2...",
    )
    sdf_parser.add_argument("--grid-size", type=int, default=10)
    sdf_parser.add_argument(
        "--bmin", type=float, nargs=3, default=[-1.0, -1.0, -1.0], help="Bounding box min"
    )
    sdf_parser.add_argument(
        "--bmax", type=float, nargs=3, default=[1.0, 1.0, 1.0], help="Bounding box max"
    )

    # Estimate Displaced Volume
    vol_parser = subparsers.add_parser(
        "estimate-volume", help="Estimates the volume of the reconstructed mesh"
    )
    vol_parser.add_argument("mesh_file", help="Path to the mesh file")

    args = parser.parse_args()

    if args.command == "generate-sdf":
        pts = []
        for i in range(0, len(args.points), 3):
            pts.append(Point3D(args.points[i], args.points[i + 1], args.points[i + 2]))
        grid = BathymetricReconstruction.generate_sdf_grid(
            pts, args.grid_size, tuple(args.bmin), tuple(args.bmax)
        )
        print(f"Generated {args.grid_size}x{args.grid_size}x{args.grid_size} SDF grid.")
        print(f"Sample value [0][0][0]: {grid[0][0][0]}")
    elif args.command == "estimate-volume":
        try:
            mesh = TriMesh.from_file(args.mesh_file)
            vol = BathymetricReconstruction.estimate_displaced_volume(mesh)
            print(f"Estimated volume: {vol}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
