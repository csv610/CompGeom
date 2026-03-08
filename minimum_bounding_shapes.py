import sys

from geometry_utils import Point
from trianglemesh.bounding import minimum_bounding_box, minimum_enclosing_circle


def parse_points(lines):
    points = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        try:
            points.append(Point(float(parts[0]), float(parts[1]), len(points)))
        except ValueError:
            continue
    return points


def format_point(point):
    return f"({point.x:.6f}, {point.y:.6f})"


def main():
    points = parse_points(sys.stdin.readlines())
    if not points:
        print("No points found in input.")
        return

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


if __name__ == "__main__":
    main()
