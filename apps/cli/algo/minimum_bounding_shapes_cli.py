from __future__ import annotations

import argparse
from compgeom import minimum_bounding_box, minimum_enclosing_circle
from .._shared import read_input_lines, parse_points, format_point


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute minimum bounding shapes for a point set."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    args = parser.parse_args(argv)
    
    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No points provided.")
        return 1
    points = parse_points(lines)
    if not points:
        print("Error: Could not parse points from input.")
        return 1
        
    circle_center, circle_radius = minimum_enclosing_circle(points)
    box = minimum_bounding_box(points)

    print("Minimum Enclosing Circle:")
    print(f"  Center: {format_point(circle_center)}")
    print(f"  Radius: {circle_radius:.6f}")

    print("\nMinimum Bounding Box:")
    print(f"  Center: {format_point(box['center'])}")
    print(f"  Width:  {box['width']:.6f}")
    print(f"  Height: {box['height']:.6f}")
    print(f"  Area:   {box['area']:.6f}")
    print(f"  Angle:  {box['angle']:.6f} radians")
    print("  Corners:")
    for index, corner in enumerate(box["corners"], start=1):
        print(f"    {index}: {format_point(corner)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
