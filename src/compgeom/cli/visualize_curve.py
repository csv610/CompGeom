import argparse
import sys
from compgeom.space_filling_curves import SpaceFillingCurves

def main():
    parser = argparse.ArgumentParser(description="Visualize space-filling curves as SVG.")
    parser.add_argument("curve", choices=["hilbert", "peano", "morton", "zigzag", "sweep"], help="Type of curve")
    parser.add_argument("--level", type=int, default=3, help="Level/order of the curve")
    parser.add_argument("--width", type=int, default=8, help="Width for zigzag/sweep")
    parser.add_argument("--height", type=int, default=8, help="Height for zigzag/sweep")
    parser.add_argument("--output", default="curve.svg", help="Output SVG filename")
    parser.add_argument("--cell_size", type=int, default=20, help="Size of each grid cell in pixels")
    
    args = parser.parse_args()
    
    if args.curve == "hilbert":
        indices = SpaceFillingCurves.hilbert(args.level)
        w = h = 2**args.level
    elif args.curve == "peano":
        indices = SpaceFillingCurves.peano(args.level)
        w = h = 3**args.level
    elif args.curve == "morton":
        indices = SpaceFillingCurves.morton(args.level)
        w = h = 2**args.level
    elif args.curve == "zigzag":
        indices = SpaceFillingCurves.zigzag(args.width, args.height)
        w, h = args.width, args.height
    elif args.curve == "sweep":
        indices = SpaceFillingCurves.sweep(args.width, args.height)
        w, h = args.width, args.height
    else:
        print(f"Unknown curve type: {args.curve}")
        sys.exit(1)
        
    SpaceFillingCurves.save_image(indices, w, h, args.output, args.cell_size)
    
    print(f"Saved {args.curve} curve visualization to {args.output}")

if __name__ == "__main__":
    main()
