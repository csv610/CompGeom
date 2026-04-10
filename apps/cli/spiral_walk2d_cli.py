from __future__ import annotations

import argparse
from compgeom import generate_spiral_path
from ._shared import handle_walk_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Spiral Walk generator")
    parser.add_argument("-x", "--width", type=int, default=10)
    parser.add_argument("-y", "--height", type=int, default=10)
    parser.add_argument("-sx", "--start_x", type=int)
    parser.add_argument("-sy", "--start_y", type=int)
    parser.add_argument("-o", "--output", help="Output filename (.json, .png, .svg)")
    parser.add_argument("-w", "--image_width", type=int, default=1024)
    args = parser.parse_args(argv)
    
    n, m = args.width, args.height
    print(f"--- 2D Spiral Walk ({n}x{m}) ---")
    path = generate_spiral_path(n, m, args.start_x, args.start_y)
    
    # Convert (x, y) coordinates to flat indices
    path_indices = [y * n + x for x, y in path]
    
    return handle_walk_output(
        path_indices, n, m, args.output, 
        image_width=args.image_width, curve_name="spiral"
    )

if __name__ == "__main__":
    raise SystemExit(main())
