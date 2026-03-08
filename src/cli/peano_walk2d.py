import argparse, math
from grid_walks import peano_index_to_coords

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=81); parser.add_argument("--height", type=int, default=81); parser.add_argument("--level", type=int)
    args = parser.parse_args()
    level = args.level if args.level is not None else (int(math.log(min(args.width, args.height), 3)) or 1)
    num_points = 9**level
    print(f"--- 2D Peano Curve ---\nLevel: {level} ({3**level}x{3**level})")
    path = [peano_index_to_coords(i, level) for i in range(num_points)]
    start_p, end_p = path[0], path[-1]
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    print(f"\n--- Walk Results ---\nTotal Steps: {num_points-1}\nUnique Cells: {len(set(path))}\nFinal Pos: {end_p}\nDisplacement: {disp:.4f}")

if __name__ == "__main__":
    main()
