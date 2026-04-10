from __future__ import annotations

import argparse
from compgeom import generate_zigzag_path
from ._shared import handle_walk_output

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="2D Zigzag Walk generator")
    parser.add_argument("-x", "--width", type=int, default=100)
    parser.add_argument("-y", "--height", type=int, default=100)
    parser.add_argument("-o", "--output", help="Output filename (.json, .png, .svg)")
    parser.add_argument("-w", "--image_width", type=int, default=1024, help="Width of output image (pixels).")
    args = parser.parse_args(argv)

    n, m = args.width, args.height
    print(f"--- 2D Zigzag Walk ({n}x{m}) ---")
    path = generate_zigzag_path(n, m)
    
    # Convert (x, y) coordinates to flat indices
    path_indices = [y * n + x for x, y in path]
    
    return handle_walk_output(
        path_indices, n, m, args.output, 
        image_width=args.image_width, curve_name="zigzag"
    )

if __name__ == "__main__":
    raise SystemExit(main())
