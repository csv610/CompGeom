import argparse
import sys
from compgeom import Point
from compgeom import LargestEmptyCircle
from compgeom import save_png, save_svg

def main():
    parser = argparse.ArgumentParser(description="Find the largest empty circle within the convex hull.")
    parser.add_argument("--points", nargs="+", help="Point coordinates as x1 y1 x2 y2 ...", required=True)
    parser.add_argument("--output", help="Output visualization file (.svg or .png)")
    
    args = parser.parse_args()
    
    try:
        raw = [float(x) for x in args.points]
        if len(raw) % 2 != 0:
            print("Error: Points need pairs of coordinates (x1 y1).")
            sys.exit(1)
            
        points = []
        for i in range(0, len(raw), 2):
            points.append(Point(raw[i], raw[i+1], i//2))
            
    except ValueError:
        print("Error: Coordinates must be numeric.")
        sys.exit(1)
        
    if len(points) < 3:
        print("Error: Need at least 3 points to define a convex hull.")
        sys.exit(1)
        
    print(f"Finding Largest Empty Circle for {len(points)} points...")
    
    center, radius = LargestEmptyCircle.find(points)
    
    print(f"\nResults:")
    print(f"  Center: ({center.x:.6f}, {center.y:.6f})")
    print(f"  Radius: {radius:.6f}")
    
    if args.output:
        svg = LargestEmptyCircle.visualize(points, center, radius)
        if args.output.lower().endswith(".png"):
            try:
                save_png(svg, args.output)
                print(f"\nSaved visualization to {args.output}")
            except Exception as e:
                print(f"\nWarning: Could not save PNG ({e}). Saving as SVG.")
                save_svg(svg, args.output.rsplit('.', 1)[0] + ".svg")
        else:
            save_svg(svg, args.output)
            print(f"\nSaved visualization to {args.output}")

if __name__ == "__main__":
    main()
