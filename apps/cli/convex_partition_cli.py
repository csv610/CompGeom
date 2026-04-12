from __future__ import annotations

import argparse

from compgeom.polygon import convex_decompose_polygon
from compgeom.mesh.meshio import MeshImporter, MeshExporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Partition a polygon into convex pieces."
    )
    parser.add_argument("input", help="Path to input mesh file")
    parser.add_argument("output", help="Path to output mesh file")
    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    result = convex_decompose_polygon(mesh.vertices)
    MeshExporter.write(args.output, result)
    print(f"Polygon partitioned into {len(result.faces)} convex pieces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
