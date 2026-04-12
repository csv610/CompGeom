from __future__ import annotations

import argparse
import sys

from compgeom.mesh.mesh import QuadMesh
from compgeom.mesh.meshio import OBJFileHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a 2D structured quad grid.")
    parser.add_argument(
        "--nx", type=int, default=10, help="Number of cells in X direction"
    )
    parser.add_argument(
        "--ny", type=int, default=10, help="Number of cells in Y direction"
    )
    parser.add_argument(
        "--origin_x", type=float, default=0.0, help="Origin X coordinate"
    )
    parser.add_argument(
        "--origin_y", type=float, default=0.0, help="Origin Y coordinate"
    )
    parser.add_argument("--spacing", type=float, default=1.0, help="Cell spacing")
    parser.add_argument("--output", type=str, required=True, help="Output OBJ file")

    args = parser.parse_args(argv)

    if args.nx < 1 or args.ny < 1:
        print("Error: nx and ny must be at least 1")
        return 1

    mesh = QuadMesh.create_structured_mesh(
        args.nx, args.ny, args.origin_x, args.origin_y, args.spacing
    )

    print(f"Created {args.nx}x{args.ny} quad grid:")
    print(f"  Vertices: {mesh.num_nodes()}")
    print(f"  Quads: {mesh.num_faces()}")

    OBJFileHandler.write(args.output, mesh)
    print(f"Saved to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
