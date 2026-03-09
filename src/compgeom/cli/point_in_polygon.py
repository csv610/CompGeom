import sys
from compgeom.geometry import Point
from compgeom.polygon import is_point_in_polygon

def main():
    lines = sys.stdin.readlines()
    if len(lines) < 4: return
    p_parts = lines[0].strip().split()
    target = Point(float(p_parts[0]), float(p_parts[1]))
    polygon = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 2: polygon.append(Point(float(parts[0]), float(parts[1])))
    is_in = is_point_in_polygon(target, polygon)
    print(f"Point {target} is {'INSIDE' if is_in else 'OUTSIDE'} the polygon.")

if __name__ == "__main__":
    main()
