import sys

from compgeom.geometry import Point
from compgeom.medial_axis import approximate_medial_axis


def parse_polygon(lines):
    polygon = []
    for index, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        try:
            polygon.append(Point(float(parts[0]), float(parts[1]), index))
        except ValueError:
            continue
    return polygon


def format_point(point):
    return f"({point.x:.6f}, {point.y:.6f})"


def main():
    max_segment_length = float(sys.argv[1]) if len(sys.argv) > 1 else 0.25
    polygon = parse_polygon(sys.stdin.readlines())
    if len(polygon) < 3:
        print("Need at least 3 polygon vertices.")
        return

    result = approximate_medial_axis(polygon, max_segment_length=max_segment_length)
    print("Approximate Medial Axis:")
    print(f"  Boundary samples: {len(result['samples'])}")
    print(f"  Axis nodes:       {len(result['centers'])}")
    print(f"  Axis segments:    {len(result['segments'])}")
    for index, (start, end) in enumerate(result["segments"], start=1):
        print(f"  {index:3}: {format_point(start)} -> {format_point(end)}")


if __name__ == "__main__":
    main()
