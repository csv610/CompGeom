from __future__ import annotations

import argparse
import sys
from compgeom.mesh import MeshImporter, MeshExporter
from compgeom.mesh.surface.subdivision.subdivision import (
    loop_subdivision,
    catmull_clark,
    doo_sabin,
    sqrt3_subdivision,
    butterfly_subdivision,
    modified_butterfly_subdivision,
    kobbelt_subdivision,
    midedge_subdivision,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply subdivision algorithms to a surface mesh."
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to input mesh file (OBJ, OFF, STL, PLY)."
    )
    parser.add_argument(
        "-o", "--output", required=True, help="Path to output mesh file."
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        choices=[
            "loop",
            "catmull_clark",
            "doo_sabin",
            "sqrt3",
            "butterfly",
            "modified_butterfly",
            "kobbelt",
            "midedge",
        ],
        default="loop",
        help="Subdivision algorithm to apply (default: loop).",
    )
    parser.add_argument(
        "-n", "--iterations", type=int, default=1, help="Number of iterations (default: 1)."
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return 1

    print(f"Applying {args.algorithm} subdivision ({args.iterations} iterations)...")

    alg_map = {
        "loop": loop_subdivision,
        "catmull_clark": catmull_clark,
        "doo_sabin": doo_sabin,
        "sqrt3": sqrt3_subdivision,
        "butterfly": butterfly_subdivision,
        "modified_butterfly": modified_butterfly_subdivision,
        "kobbelt": kobbelt_subdivision,
        "midedge": midedge_subdivision,
    }

    subdivision_func = alg_map[args.algorithm]
    
    try:
        refined_mesh = subdivision_func(mesh, iterations=args.iterations)
    except Exception as e:
        print(f"Error during subdivision: {e}")
        return 1

    try:
        MeshExporter.write(args.output, refined_mesh)
        print(f"Refined mesh written to {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
