from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter
from compgeom.mesh.mesh_geometry import MeshGeometry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calculate face and vertex normals for a mesh."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", help="Path to output text file for normal values."
    )
    parser.add_argument(
        "-t", "--type", choices=["face", "vertex", "both"], default="both",
        help="Type of normals to calculate (default: both)."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    results = {}
    if args.type in ["face", "both"]:
        print("Calculating face normals...")
        f_normals = MeshGeometry.face_normals(mesh)
        results["face"] = f_normals
        print(f"  Computed {len(f_normals)} face normals.")

    if args.type in ["vertex", "both"]:
        print("Calculating vertex normals...")
        v_normals = MeshGeometry.vertex_normals(mesh)
        results["vertex"] = v_normals
        print(f"  Computed {len(v_normals)} vertex normals.")

    try:
        if args.output:
            with open(args.output, "w") as f:
                if "face" in results:
                    f.write("# Face Normals (nx, ny, nz)\n")
                    for n in results["face"]:
                        f.write(f"{n.x:.8f} {n.y:.8f} {n.z:.8f}\n")
                if "vertex" in results:
                    f.write("# Vertex Normals (nx, ny, nz)\n")
                    for n in results["vertex"]:
                        f.write(f"{n.x:.8f} {n.y:.8f} {n.z:.8f}\n")
            print(f"Normal values written to {args.output}")
        else:
            # Print a few to stdout if no output file
            if "face" in results:
                print("Top 5 Face Normals:")
                for i in range(min(5, len(results["face"]))):
                    n = results["face"][i]
                    print(f"  {i}: {n.x:.4f}, {n.y:.4f}, {n.z:.4f}")
            if "vertex" in results:
                print("Top 5 Vertex Normals:")
                for i in range(min(5, len(results["vertex"]))):
                    n = results["vertex"][i]
                    print(f"  {i}: {n.x:.4f}, {n.y:.4f}, {n.z:.4f}")
    except Exception as e:
        print(f"Error saving results: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
