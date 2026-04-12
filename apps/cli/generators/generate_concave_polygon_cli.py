from __future__ import annotations

import argparse
from compgeom.polygon import generate_concave_polygon
from compgeom.mesh.meshio import MeshExporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate concave polygons.")
    parser.add_argument(
        "-n", "--num_points", type=int, default=15, help="Number of vertices"
    )
    parser.add_argument(
        "-o", "--output", default="concave_polygon.off", help="Output polygon file"
    )
    args = parser.parse_args(argv)

    poly = generate_concave_polygon(args.num_points)

    MeshExporter.write(args.output, poly)


if __name__ == "__main__":
    raise SystemExit(main())
