from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.mesh.surface.mesh_clipper import MeshClipper


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Slice a mesh with a plane."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "--origin", nargs=3, type=float, default=[0.0, 0.0, 0.0],
        help="Point on the slicing plane (x y z)."
    )
    parser.add_argument(
        "--normal", nargs=3, type=float, default=[0.0, 0.0, 1.0],
        help="Normal vector of the slicing plane (nx ny nz)."
    )
    parser.add_argument(
        "-a", "--above", required=True, help="Path to save the part above the plane."
    )
    parser.add_argument(
        "-b", "--below", required=True, help="Path to save the part below the plane."
    )
    parser.add_argument(
        "--no-cap", action="store_false", dest="cap",
        help="Do not cap the holes created by the slice."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    print(f"Slicing mesh with plane at origin={args.origin}, normal={args.normal}...")
    
    try:
        mesh_above, mesh_below = MeshClipper.clip(
            mesh, 
            tuple(args.origin), 
            tuple(args.normal), 
            cap=args.cap
        )
    except Exception as e:
        print(f"Error during slicing: {e}")
        return 1

    try:
        MeshExporter.write(args.above, mesh_above)
        print(f"  Part above written to {args.above}")
        
        MeshExporter.write(args.below, mesh_below)
        print(f"  Part below written to {args.below}")
    except Exception as e:
        print(f"Error writing output files: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
