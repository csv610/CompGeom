from __future__ import annotations

import argparse

from compgeom.kernel import Point2D
from compgeom.mesh_io import  MeshExporter
from compgeom.polygon import generate_convex_polygon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a random convex polygon.")
    parser.add_argument(
        "-n",
        "--num_points",
        type=int,
        default=20,
        help="Number of random samples used to generate the polygon.",
    )
    parser.add_argument(
        "-s",
        "--sampling",
        type=str,
        default="circle",
        choices=["random", "circle"],
        help="Sampling method: 'random' (uniform) or 'circle' (on circumcircle).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="convex_polygon.off",
        help="Path to output OFF file.",
    )
    args = parser.parse_args(argv)

    hull = generate_convex_polygon(args.num_points, sampling=args.sampling)

    MeshExporter.to_file(args.output, hull)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
