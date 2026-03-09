import random
import argparse

from compgeom import Point
from compgeom import welzl
from ._shared import read_nonempty_stdin_lines


def _parse_points(lines: list[str]) -> list[Point]:
    points: list[Point] = []
    for line_number, line in enumerate(lines, start=1):
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"Line {line_number}: expected 2 numbers, got {len(parts)}.")
        try:
            points.append(Point(float(parts[0]), float(parts[1])))
        except ValueError as exc:
            raise ValueError(f"Line {line_number}: invalid numeric input.") from exc
    return points


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute the smallest enclosing circle for 2D points read from stdin."
    )
    parser.parse_args()

    try:
        points = _parse_points(read_nonempty_stdin_lines())
    except ValueError as exc:
        print(f"Invalid input: {exc}")
        return 1

    if not points:
        print("No valid points provided.")
        return 1

    random.shuffle(points)
    center, radius = welzl(list(points), [])
    print(f"Smallest Enclosing Circle:\n  Center: ({center.x:.6f}, {center.y:.6f})\n  Radius: {radius:.6f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
