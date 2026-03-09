import sys

from compgeom.geometry import Point
from compgeom.points_sampling import PointSampler


def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    if not lines:
        return

    try:
        width, height = map(float, lines[0].split()[:2])
        n_points = int(lines[1]) if len(lines) > 1 else 100
    except (ValueError, IndexError):
        print("Invalid input.")
        return

    points = PointSampler.in_rectangle(width, height, n_points)
    print(
        f"Generated {len(points)} points in rectangle centered at (0.0000, 0.0000), "
        f"width {width:.4f}, height {height:.4f}:"
    )
    for point in points:
        print(f"  ({point.x:.6f}, {point.y:.6f})")


if __name__ == "__main__":
    main()
