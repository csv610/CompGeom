import argparse, math
from compgeom.walks import generate_spiral_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=10); parser.add_argument("--height", type=int, default=10)
    parser.add_argument("--start_x", type=int); parser.add_argument("--start_y", type=int)
    args = parser.parse_args()
    print(f"--- 2D Spiral Walk ({args.width}x{args.height}) ---")
    path = generate_spiral_path(args.width, args.height, args.start_x, args.start_y)
    dist = sum(math.sqrt((path[i][0]-path[i-1][0])**2 + (path[i][1]-path[i-1][1])**2) for i in range(1, len(path)))
    print(f"\n--- Walk Results ---\nTotal cells: {len(path)}\nDistance: {dist:.4f}\nFinal Pos: {path[-1]}")

if __name__ == "__main__":
    main()
