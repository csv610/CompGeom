from __future__ import annotations

from compgeom import minimum_bounding_box, minimum_enclosing_circle
from compgeom.cli._shared import demo_points, format_point


def main() -> int:
    points = demo_points()
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
