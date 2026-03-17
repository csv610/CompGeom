import argparse
import sys
from compgeom import Point2D
from compgeom import DistanceMapSolver
from compgeom import OBJFileHandler
from compgeom import save_png, save_svg

def read_polygon(args):
    if args.input:
        print(f"Reading polygon from {args.input}...")
        mesh = OBJFileHandler.read(args.input)
        vertices = mesh.vertices
        return [Point2D(v.x, v.y) for v in vertices]
    
    if args.poly:
        try:
            raw = [float(x) for x in args.poly]
            return [Point2D(raw[i], raw[i+1]) for i in range(0, len(raw), 2)]
        except Exception as e:
            print(f"Error parsing coordinates: {e}")
            sys.exit(1)
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Calculate distance map from polygon boundaries.")
    parser.add_argument("--input", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--res", type=int, default=100, help="Grid resolution")
    parser.add_argument("--output", default="distance_map.png", help="Output visualization file")
    
    args = parser.parse_args()
    
    polygon = read_polygon(args)
    if not polygon:
        print("Error: No polygon provided. Use --input or --poly.")
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
