import sys

from compgeom import Point
from compgeom.points_sampling import PointSampler


def main():
    lines = [line.strip() for line in sys.stdin if line.strip()]
    if not lines:
        return

    try:
        x, y, radius = map(float, lines[0].split()[:3])
        n_points = int(lines[1]) if len(lines) > 1 else 100
    except (ValueError, IndexError):
        print("Invalid input.")
        return

    points = PointSampler.in_circle(Point(x, y), radius, n_points)
    print(f"Generated {len(points)} points in circle centered at ({x:.4f}, {y:.4f}) with radius {radius:.4f}:")
    for point in points:
        print(f"  ({point.x:.6f}, {point.y:.6f})")


if __name__ == "__main__":
    main()
