from __future__ import annotations

import argparse
from compgeom import simulate_random_walk_3d

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="3D Grid Random Walker simulator")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--depth", type=int, default=100)
    parser.add_argument("--start_x", type=int)
    parser.add_argument("--start_y", type=int)
    parser.add_argument("--start_z", type=int)
    parser.add_argument("--steps", type=int, default=10000)
    args = parser.parse_args(argv)
    
    n, m, l = args.width, args.height, args.depth
    sx = args.start_x if args.start_x is not None else n // 2
    sy = args.start_y if args.start_y is not None else m // 2
    sz = args.start_z if args.start_z is not None else l // 2
    
    print(f"--- 3D Grid Random Walker ({n}x{m}x{l}) ---")
    print(f"Starting at: ({sx}, {sy}, {sz})")
    print(f"Steps: {args.steps}")
    
    res = simulate_random_walk_3d(n, m, l, sx, sy, sz, args.steps)
    
    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {res['steps']}")
    print(f"Unique Cells: {res['unique_cells']}")
    print(f"Final Pos: {res['final_pos']}")
    print(f"Displacement: {res['displacement']:.4f}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
