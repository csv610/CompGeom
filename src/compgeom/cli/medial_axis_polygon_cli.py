from __future__ import annotations

import argparse

from compgeom.kernel import Point2D
from compgeom.mesh import MeshImporter
from compgeom.polygon import approximate_medial_axis


def read_polygon(args) -> list | None:
    if args.obj:
        print(f"Reading polygon from {args.obj}...")
        try:
            mesh = OBJFileHandler.read(args.obj)
            return [Point2D(v.x, v.y, i) for i, v in enumerate(mesh.vertices)]
        except Exception as e:
            print(f"Error reading OBJ file: {e}")
            return None

    if args.off:
        print(f"Reading polygon from {args.off}...")
        try:
            mesh = OFFFileHandler.read(args.off)
            return [Point2D(v.x, v.y, i) for i, v in enumerate(mesh.vertices)]
        except Exception as e:
            print(f"Error reading OFF file: {e}")
            return None

    lines = read_input_lines(args.input)
    if lines:
        return parse_points(lines)

    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Approximate the medial axis of a polygon."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to input file (optional, reads from stdin if omitted).",
    )
    parser.add_argument("--obj", help="Path to input OBJ file defining the polygon.")
    parser.add_argument("--off", help="Path to input OFF file defining the polygon.")
    parser.add_argument(
        "--resolution", type=float, default=0.25, help="Boundary sampling resolution."
    )
    args = parser.parse_args(argv)

    polygon = read_polygon(args)
    if not polygon:
        print(
            "Error: No input polygon provided. Use --obj, --off, --input, or pipe vertices to stdin."
        )
        return 1

    resolution = args.resolution
    result = approximate_medial_axis(polygon, resolution=resolution)
    print("Approximate Medial Axis:")
    print(f"  Boundary samples: {len(result['samples'])}")
    print(f"  Axis nodes:       {len(result['centers'])}")
    print(f"  Axis segments:    {len(result['segments'])}")
    for index, (start, end) in enumerate(result["segments"], start=1):
        print(f"  {index:3}: {format_point(start)} -> {format_point(end)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
