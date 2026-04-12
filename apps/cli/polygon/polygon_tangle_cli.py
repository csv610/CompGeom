from __future__ import annotations

import argparse

from compgeom.polygon.polygon_tangle import tangle_polygon
from compgeom.mesh.meshio import MeshImporter, MeshExporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Randomize polygon vertex positions within bounding box."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to input OFF file defining the polygon",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to output OFF file for tangled polygon",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility.",
    )
    parser.add_argument(
        "-j",
        "--jitter",
        type=float,
        default=0.1,
        help="Maximum jitter as fraction of bounding box size (0.0 to 1.0).",
    )
    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading OFF file: {e}")
        return 1

    tangled = tangle_polygon(mesh, seed=args.seed, max_jitter=args.jitter)

    try:
        MeshExporter.write(args.output, tangled)
        print(f"Tangled mesh written to {args.output}")
    except Exception as e:
        print(f"Error writing OFF file: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
