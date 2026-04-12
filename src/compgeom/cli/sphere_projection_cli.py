from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compgeom.mesh import from_file, to_file
from compgeom.mesh.surface.surface_mesh import SurfaceMesh
from compgeom.mesh.surface.mesh_sphere_projection import project


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Project a 3D mesh onto a sphere.")
    parser.add_argument("input", help="Input mesh file path.")
    parser.add_argument("output", help="Output mesh file path.")
    parser.add_argument(
        "--smooth",
        type=int,
        default=0,
        help="Number of smoothing iterations (default: 0).",
    )

    args = parser.parse_args(argv)

    print(f"Reading mesh from {args.input}...")
    try:
        mesh = from_file(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces.")

    result = project(mesh, smoothing_steps=args.smooth)
    print(f"Projected mesh onto bounding sphere with {args.smooth} smoothing steps.")

    print(f"Writing mesh to {args.output}...")
    try:
        to_file(args.output, result)
        print("Projection successful.")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
