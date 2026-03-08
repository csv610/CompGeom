import sys
from geometry_utils import Point
from proximity_utils import do_intersect

def main():
    lines = sys.stdin.readlines()
    if len(lines) < 2: return
    try:
        parts1, parts2 = lines[0].split(), lines[1].split()
        p1, q1 = Point(float(parts1[0]), float(parts1[1])), Point(float(parts1[2]), float(parts1[3]))
        p2, q2 = Point(float(parts2[0]), float(parts2[1])), Point(float(parts2[2]), float(parts2[3]))
    except (ValueError, IndexError):
        print("Invalid input."); return
    intersect = do_intersect(p1, q1, p2, q2)
    print(f"Segment 1: ({p1.x}, {p1.y}) to ({q1.x}, {q1.y})\nSegment 2: ({p2.x}, {p2.y}) to ({q2.x}, {q2.y})\nResult: Intersect? {intersect}")

if __name__ == "__main__":
    main()
