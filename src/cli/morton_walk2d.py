import argparse, math
from grid_walks import morton_index_to_coords

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=128); parser.add_argument("--height", type=int, default=128); parser.add_argument("--steps", type=int)
    args = parser.parse_args()
    num_points = args.steps if args.steps is not None else args.width * args.height
    print(f"--- 2D Morton Curve ---\nGrid: {args.width}x{args.height}")
    path = [p for i in range(num_points) for p in [morton_index_to_coords(i)] if p[0] < args.width and p[1] < args.height]
    dist = sum(math.sqrt((path[i][0]-path[i-1][0])**2 + (path[i][1]-path[i-1][1])**2) for i in range(1, len(path)))
    start_p, end_p = path[0] if path else (0,0), path[-1] if path else (0,0)
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    print(f"\n--- Walk Results ---\nPoints: {len(path)}\nDistance: {dist:.4f}\nUnique Cells: {len(set(path))}\nFinal Pos: {end_p}\nDisplacement: {disp:.4f}")

if __name__ == "__main__":
    main()
