import argparse, sys
from compgeom import simulate_random_walk_2d

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--start_x", type=int); parser.add_argument("--start_y", type=int)
    parser.add_argument("--steps", type=int)
    args = parser.parse_args()
    n, m = args.width, args.height
    sx = args.start_x if args.start_x is not None else n // 2
    sy = args.start_y if args.start_y is not None else m // 2
    print(f"--- Grid Random Walker ({n}x{m}) ---\nStarting at: ({sx}, {sy})")
    res = simulate_random_walk_2d(n, m, sx, sy, args.steps)
    print(f"\n--- Walk Results ---\nTotal Steps: {res['steps']}\nUnique Cells: {res['unique_cells']}\nFinal Pos: {res['final_pos']}\nDisplacement: {res['displacement']:.4f}")

if __name__ == "__main__":
    main()
