import sys
from compgeom import Point
from compgeom import min_dist_convex_polygons

def main():
    lines, idx = sys.stdin.readlines(), 0
    if not lines: return
    def read_poly():
        nonlocal idx
        while idx < len(lines) and not lines[idx].strip(): idx += 1
        if idx >= len(lines): return None
        n = int(lines[idx].strip()); idx += 1; poly = []
        for _ in range(n):
            parts = lines[idx].split(); poly.append(Point(float(parts[0]), float(parts[1]))); idx += 1
        return poly
    p1, p2 = read_poly(), read_poly()
    if p1 and p2:
        dist = min_dist_convex_polygons(p1, p2)
        print(f"Minimum distance between polygons: {dist:.6f}")

if __name__ == "__main__":
    main()
