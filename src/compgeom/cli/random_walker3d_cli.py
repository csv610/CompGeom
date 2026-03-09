import argparse, sys
from compgeom import simulate_random_walk_3d

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=100); parser.add_argument("--height", type=int, default=100); parser.add_argument("--depth", type=int, default=100)
    parser.add_argument("--start_x", type=int); parser.add_argument("--start_y", type=int); parser.add_argument("--start_z", type=int)
    parser.add_argument("--steps", type=int)
    args = parser.parse_args()
    n, m, l = args.width, args.height, args.depth
    sx = args.start_x if args.start_x is not None else n // 2
    sy = args.start_y if args.start_y is not None else m // 2
    sz = args.start_z if args.start_z is not None else l // 2
    print(f"--- 3D Grid Random Walker ({n}x{m}x{l}) ---\nStarting at: ({sx}, {sy}, {sz})")
    res = simulate_random_walk_3d(n, m, l, sx, sy, sz, args.steps)
    print(f"\n--- Walk Results ---\nTotal Steps: {res['steps']}\nUnique Cells: {res['unique_cells']}\nFinal Pos: {res['final_pos']}\nDisplacement: {res['displacement']:.4f}")

if __name__ == "__main__":
    main()
