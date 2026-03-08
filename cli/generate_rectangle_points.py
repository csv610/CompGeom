import sys

from geometry_utils import Point
from trianglemesh.sampling import generate_points_in_rectangle


def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    if not lines:
        return

    try:
        width, height = map(float, lines[0].split()[:2])
        n_points = int(lines[1]) if len(lines) > 1 else 100
        if len(lines) > 2:
            center_x, center_y = map(float, lines[2].split()[:2])
            center = Point(center_x, center_y)
        else:
            center = Point(0.0, 0.0)
    except (ValueError, IndexError):
        print("Invalid input.")
        return

    points = generate_points_in_rectangle(width, height, n_points, center)
    print(
        f"Generated {len(points)} points in rectangle centered at "
        f"({center.x:.4f}, {center.y:.4f}), width {width:.4f}, height {height:.4f}:"
    )
    for point in points:
        print(f"  ({point.x:.6f}, {point.y:.6f})")


if __name__ == "__main__":
    main()
