from __future__ import annotations

import argparse

from compgeom.kernel import Point2D
from compgeom.mesh.meshio import MeshImporter, MeshExporter
from compgeom.polygon import approximate_medial_axis


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Approximate the medial axis of a polygon."
    )
    parser.add_argument("input", help="Path to input mesh file")
    parser.add_argument("output", help="Path to output mesh file")
    parser.add_argument(
        "--resolution", type=float, default=0.25, help="Boundary sampling resolution."
    )
    args = parser.parse_args(argv)

    try:
        mesh = MeshImporter.read(args.input)
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    polygon = [Point2D(v.x, v.y, i) for i, v in enumerate(mesh.vertices)]
    result = approximate_medial_axis(polygon, resolution=args.resolution)

    MeshExporter.write(args.output, result["centers"], edges=result["segments"])
    print("Approximate Medial Axis:")
    print(f"  Boundary samples: {len(result['samples'])}")
    print(f"  Axis nodes:       {len(result['centers'])}")
    print(f"  Axis segments:    {len(result['segments'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
