from __future__ import annotations

import argparse
from compgeom import approximate_medial_axis
from ._shared import read_input_lines, parse_points, format_point


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Approximate the medial axis of a polygon.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--resolution", type=float, default=0.25, help="Boundary sampling resolution.")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input polygon provided.")
        return 1
    polygon = parse_points(lines)
    if not polygon:
        print("Error: Could not parse polygon from input.")
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
