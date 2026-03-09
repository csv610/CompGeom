import argparse, sys
from compgeom import simulate_saw_2d

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=100); parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--start_x", type=int); parser.add_argument("--start_y", type=int)
    args = parser.parse_args()
    n, m = args.width, args.height
    sx = args.start_x if args.start_x is not None else n // 2
    sy = args.start_y if args.start_y is not None else m // 2
    print(f"--- 2D Self-Avoiding Walk ({n}x{m}) ---\nStarting at: ({sx}, {sy})")
    res = simulate_saw_2d(n, m, sx, sy)
    print(f"\n--- Walk Results ---\nTermination: {res['reason']}\nTotal Steps: {res['steps']}\nUnique Cells: {res['unique_cells']}\nFinal Pos: {res['final_pos']}\nDisplacement: {res['displacement']:.4f}")

if __name__ == "__main__":
    main()
