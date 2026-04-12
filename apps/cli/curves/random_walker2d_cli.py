from __future__ import annotations

import argparse
from compgeom import simulate_random_walk_2d

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grid Random Walker simulator")
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--start_x", type=int)
    parser.add_argument("--start_y", type=int)
    parser.add_argument("--steps", type=int, default=10000)
    args = parser.parse_args(argv)
    
    n, m = args.width, args.height
    sx = args.start_x if args.start_x is not None else n // 2
    sy = args.start_y if args.start_y is not None else m // 2
    
    print(f"--- Grid Random Walker ({n}x{m}) ---")
    print(f"Starting at: ({sx}, {sy})")
    print(f"Steps: {args.steps}")
    
    res = simulate_random_walk_2d(n, m, sx, sy, args.steps)
    
    print(f"\n--- Walk Results ---")
    print(f"Total Steps: {res['steps']}")
    print(f"Unique Cells: {res['unique_cells']}")
    print(f"Final Pos: {res['final_pos']}")
    print(f"Displacement: {res['displacement']:.4f}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
