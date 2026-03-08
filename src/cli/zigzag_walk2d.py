import argparse, math
from grid_walks import generate_zigzag_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=100); parser.add_argument("--height", type=int, default=100)
    args = parser.parse_args()
    n, m = args.width, args.height
    print(f"--- 2D Zigzag Walk ({n}x{m}) ---")
    path = generate_zigzag_path(n, m)
    dist = sum(math.sqrt((path[i][0]-path[i-1][0])**2 + (path[i][1]-path[i-1][1])**2) for i in range(1, len(path)))
    start_p, end_p = path[0], path[-1]
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    print(f"\n--- Walk Results ---\nPoints: {len(path)}\nDistance: {dist:.4f}\nUnique Cells: {len(set(path))}\nFinal Pos: {end_p}\nDisplacement: {disp:.4f}")

if __name__ == "__main__":
    main()
