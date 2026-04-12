from __future__ import annotations

import argparse
import json
import math

from compgeom.algo import SpaceFillingCurves


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Space-filling curve generator")
    parser.add_argument(
        "curve",
        choices=[
            "hilbert",
            "peano",
            "morton",
            "zigzag",
            "sweep",
            "spiral",
            "hilbert3d",
            "morton3d",
        ],
        help="Type of curve",
    )
    parser.add_argument(
        "-o",
        "--order",
        type=int,
        default=3,
        help="Order/level for hilbert/peano/morton",
    )
    parser.add_argument(
        "-w", "--width", type=int, default=8, help="Width for zigzag/sweep/spiral"
    )
    parser.add_argument(
        "-H", "--height", type=int, default=8, help="Height for zigzag/sweep/spiral"
    )
    parser.add_argument("-f", "--output", help="Output filename (.json, .png)")
    parser.add_argument(
        "--image_size", type=int, default=1024, help="Image size in pixels"
    )
    args = parser.parse_args(argv)

    curve = args.curve
    indices = []

    if curve == "hilbert":
        indices = SpaceFillingCurves.hilbert(args.order)
        w = h = 2**args.order
    elif curve == "peano":
        indices = SpaceFillingCurves.peano(args.order)
        w = h = 3**args.order
    elif curve == "morton":
        indices = SpaceFillingCurves.morton(args.order)
        w = h = 2**args.order
    elif curve == "zigzag":
        indices = SpaceFillingCurves.zigzag(args.width, args.height)
        w, h = args.width, args.height
    elif curve == "sweep":
        indices = SpaceFillingCurves.sweep(args.width, args.height)
        w, h = args.width, args.height
    elif curve == "spiral":
        path = SpaceFillingCurves.spiral(args.width, args.height)
        indices = [y * args.width + x for x, y in path]
        w, h = args.width, args.height
    elif curve == "hilbert3d":
        indices = SpaceFillingCurves.hilbert_3d(args.order)
        print(
            f"3D Hilbert order {args.order}: {len(indices)} points, grid size {2**args.order}"
        )
        if args.output:
            if args.output.endswith(".json"):
                data = {"curve": "hilbert3d", "order": args.order, "path": indices}
                with open(args.output, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to {args.output}")
            else:
                print("3D curves only support JSON output")
        return 0
    elif curve == "morton3d":
        indices = SpaceFillingCurves.morton_3d(args.order)
        print(
            f"3D Morton level {args.order}: {len(indices)} points, grid size {2**args.order}"
        )
        if args.output:
            if args.output.endswith(".json"):
                data = {"curve": "morton3d", "order": args.order, "path": indices}
                with open(args.output, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"Saved to {args.output}")
            else:
                print("3D curves only support JSON output")
        return 0

    print(f"--- {curve.upper()} Curve ---")
    print(f"Grid: {w}x{h}, Points: {len(indices)}")

    if args.output:
        if args.output.endswith(".png"):
            cell_size = max(1, args.image_size // max(w, h))
            SpaceFillingCurves.save_image(indices, w, h, args.output, cell_size)
            print(f"Saved image to {args.output}")
        elif args.output.endswith(".json"):
            coords = [(idx % w, idx // w) for idx in indices]
            data = {
                "curve": curve,
                "width": w,
                "height": h,
                "indices": indices,
                "coordinates": coords,
            }
            with open(args.output, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved JSON to {args.output}")
        else:
            print("Unsupported format. Use .json or .png")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
