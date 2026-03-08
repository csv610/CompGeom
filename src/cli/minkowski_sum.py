import sys
from geometry_utils import Point
from proximity_utils import minkowski_sum

def main():
    lines, idx = sys.stdin.readlines(), 0
    if not lines: return
    def read_poly():
        nonlocal idx
        while idx < len(lines) and not lines[idx].strip(): idx += 1
        if idx >= len(lines): return None
        try:
            n = int(lines[idx].strip()); idx += 1; poly = []
            for _ in range(n):
                parts = lines[idx].split(); poly.append(Point(float(parts[0]), float(parts[1]))); idx += 1
            return poly
        except (ValueError, IndexError): return None
    p1, p2 = read_poly(), read_poly()
    if p1 and p2:
        res = minkowski_sum(p1, p2)
        print(f"Minkowski Sum result ({len(res)} vertices):")
        for p in res: print(f"  ({p.x:.4f}, {p.y:.4f})")

if __name__ == "__main__":
    main()
