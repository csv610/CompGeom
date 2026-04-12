from __future__ import annotations

import argparse
import json
from compgeom import pack_circles
from compgeom.mesh.meshio import MeshImporter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pack circles into a closed polygon.")
    parser.add_argument("input", help="Path to input mesh file")
    parser.add_argument(
        "-r", "--radius", type=float, default=0.5, help="Radius of circles to pack"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="circle_packing.json",
        help="Output JSON file",
    )

    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    result = pack_circles(mesh, args.radius)

    output = {
        "centers": [{"x": c.x, "y": c.y} for c in result.centers],
        "efficiency": result.efficiency,
        "radius": result.radius,
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Saved results to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
