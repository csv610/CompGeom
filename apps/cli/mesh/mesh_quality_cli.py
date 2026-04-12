from __future__ import annotations

import argparse
import sys
import numpy as np
from compgeom.mesh import MeshImporter
from compgeom.mesh.surface.mesh_quality import MeshQuality
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute geometric quality metrics for a triangle mesh."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input triangle mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", help="Path to output text file for per-face quality values."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    if not isinstance(mesh, TriMesh):
        print("Warning: Input mesh is not a TriMesh. Attempting to triangulate...")
        try:
            if hasattr(mesh, "triangulate"):
                mesh = mesh.triangulate()
            else:
                print("Error: Could not triangulate mesh.")
                return 1
        except Exception as e:
            print(f"Error during triangulation: {e}")
            return 1

    print("Computing aspect ratios...")
    ratios = MeshQuality.aspect_ratio(mesh)
    valid_ratios = [r for r in ratios if r != float('inf')]
    print(f"  Mean Aspect Ratio: {np.mean(valid_ratios):.6f} (Ideal: 1.0)")
    print(f"  Max Aspect Ratio:  {np.max(valid_ratios):.6f}")
    print(f"  Min Aspect Ratio:  {np.min(valid_ratios):.6f}")

    print("Computing angles...")
    angles = MeshQuality.min_max_angles(mesh)
    min_angles = [a[0] for a in angles]
    max_angles = [a[1] for a in angles]
    print(f"  Average Min Angle: {np.mean(min_angles):.2f}°")
    print(f"  Smallest Angle:    {np.min(min_angles):.2f}°")
    print(f"  Average Max Angle: {np.mean(max_angles):.2f}°")
    print(f"  Largest Angle:     {np.max(max_angles):.2f}°")

    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write("FaceIdx\tAspectRatio\tMinAngle\tMaxAngle\n")
                for i in range(len(ratios)):
                    f.write(f"{i}\t{ratios[i]:.6f}\t{angles[i][0]:.2f}\t{angles[i][1]:.2f}\n")
            print(f"Quality values written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
