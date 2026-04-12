from __future__ import annotations

import argparse
import sys
import numpy as np
from compgeom.mesh import MeshImporter
from compgeom.mesh.surface.curvature import MeshCurvature
from compgeom.mesh.surface.trimesh.trimesh import TriMesh


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calculate Gaussian and Mean curvature for a triangle mesh."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input triangle mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", help="Path to output text file for curvature values."
    )
    parser.add_argument(
        "-t", "--type", choices=["gaussian", "mean", "both"], default="both",
        help="Type of curvature to calculate (default: both)."
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

    results = {}
    if args.type in ["gaussian", "both"]:
        print("Calculating Gaussian curvature...")
        gaussian = MeshCurvature.gaussian_curvature(mesh)
        results["gaussian"] = gaussian
        print(f"  Mean: {np.mean(gaussian):.6f}")
        print(f"  Std:  {np.std(gaussian):.6f}")
        print(f"  Min:  {np.min(gaussian):.6f}")
        print(f"  Max:  {np.max(gaussian):.6f}")

    if args.type in ["mean", "both"]:
        print("Calculating Mean curvature...")
        mean_curv = MeshCurvature.mean_curvature(mesh)
        results["mean"] = mean_curv
        print(f"  Mean: {np.mean(mean_curv):.6f}")
        print(f"  Std:  {np.std(mean_curv):.6f}")
        print(f"  Min:  {np.min(mean_curv):.6f}")
        print(f"  Max:  {np.max(mean_curv):.6f}")

    if args.output:
        try:
            with open(args.output, "w") as f:
                header = []
                if "gaussian" in results: header.append("Gaussian")
                if "mean" in results: header.append("Mean")
                f.write("\t".join(header) + "\n")
                
                num_v = len(mesh.vertices)
                for i in range(num_v):
                    line = []
                    if "gaussian" in results: line.append(f"{results['gaussian'][i]:.10f}")
                    if "mean" in results: line.append(f"{results['mean'][i]:.10f}")
                    f.write("\t".join(line) + "\n")
            print(f"Curvature values written to {args.output}")
        except Exception as e:
            print(f"Error writing output file: {e}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
