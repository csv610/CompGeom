import sys
from compgeom import Point
from compgeom import get_voronoi_cells, get_circle_boundary, get_square_boundary

def main():
    points = []
    lines = sys.stdin.readlines()
    if not lines: return
    boundary_type = sys.argv[1].lower() if len(sys.argv) > 1 else "square"
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                x, y = float(parts[0]), float(parts[1])
                points.append(Point(x, y, len(points)))
            except ValueError: continue
    if not points:
        print("No valid points provided."); return
    boundary = get_circle_boundary() if boundary_type == "circle" else get_square_boundary()
    print(f"Using {boundary_type} boundary.")
    cells = get_voronoi_cells(points, boundary)
    print(f"Voronoi Diagram: {len(cells)} cells generated.")
    for p, cell in cells:
        print(f"\nPoint {p.id} at ({p.x}, {p.y}) Cell Vertices:")
        for v in cell: print(f"  ({v.x:.4f}, {v.y:.4f})")

if __name__ == "__main__":
    main()
