from __future__ import annotations

import argparse
import math
from compgeom import generate_zigzag_path, SpaceFillingCurves

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Zigzag Walk generator")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--height", type=int, default=100)
    parser.add_argument("--output", help="Output visualization filename (SVG)")
    parser.add_argument("--cell_size", type=float, default=5.0, help="Size of each cell in pixels")
    args = parser.parse_args(argv)

    n, m = args.width, args.height
    print(f"--- 2D Zigzag Walk ({n}x{m}) ---")
    path = generate_zigzag_path(n, m)
    dist = sum(math.sqrt((path[i][0]-path[i-1][0])**2 + (path[i][1]-path[i-1][1])**2) for i in range(1, len(path)))
    start_p, end_p = path[0], path[-1]
    disp = math.sqrt((end_p[0]-start_p[0])**2 + (end_p[1]-start_p[1])**2)
    
    print(f"\n--- Walk Results ---")
    print(f"Points: {len(path)}")
    print(f"Distance: {dist:.4f}")
    print(f"Unique Cells: {len(set(path))}")
    print(f"Final Pos: {end_p}")
    print(f"Displacement: {disp:.4f}")

    if args.output:
        indices = [y * n + x for x, y in path]
        SpaceFillingCurves.save_image(indices, n, m, args.output, args.cell_size)
        print(f"\nSaved visualization to {args.output}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
