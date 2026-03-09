import argparse
import sys
from compgeom.geometry import Point
from compgeom.distance_map import DistanceMapSolver
from compgeom.visualization import save_png, save_svg

def main():
    parser = argparse.ArgumentParser(description="Calculate distance map from polygon boundaries.")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...", required=True)
    parser.add_argument("--res", type=int, default=100, help="Grid resolution")
    parser.add_argument("--output", default="distance_map.png", help="Output visualization file")
    
    args = parser.parse_args()
    
    try:
        raw = [float(x) for x in args.poly]
        polygon = [Point(raw[i], raw[i+1]) for i in range(0, len(raw), 2)]
    except Exception as e:
        print(f"Error parsing polygon: {e}")
        sys.exit(1)
        
    print(f"Solving Eikonal equation for polygon with {len(polygon)} vertices...")
    grid, extent = DistanceMapSolver.solve(polygon, resolution=args.res)
    
    print(f"Grid size: {len(grid)} x {len(grid[0])}")
    
    svg = DistanceMapSolver.visualize_svg(grid, extent)
    
    if args.output.lower().endswith(".png"):
        try:
            save_png(svg, args.output)
            print(f"Saved distance map to {args.output}")
        except Exception as e:
            print(f"Could not save PNG ({e}). Saving SVG.")
            save_svg(svg, args.output.rsplit('.', 1)[0] + ".svg")
    else:
        save_svg(svg, args.output)

if __name__ == "__main__":
    main()
