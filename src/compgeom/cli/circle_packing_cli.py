import argparse
import sys
from compgeom import Point2D
from compgeom import CirclePacker
from compgeom import OBJFileHandler
from compgeom import save_png, save_svg

def read_polygon(args):
    if hasattr(args, 'input') and args.input:
        print(f"Reading polygon from {args.input}...")
        vertices, _ = OBJFileHandler.read(args.input)
        # Ensure they are 2D points for circle packing
        return [Point2D(v.x, v.y) for v in vertices]
    
    if hasattr(args, 'poly') and args.poly:
        try:
            raw = [float(x) for x in args.poly]
            if len(raw) % 2 != 0:
                print("Error: Polygon needs pairs of coordinates (x1 y1).")
                sys.exit(1)
            return [Point2D(raw[i], raw[i+1]) for i in range(0, len(raw), 2)]
        except ValueError:
            print("Error: Coordinates must be numeric.")
            sys.exit(1)
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Pack circles into a closed polygon.")
    parser.add_argument("--input", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--radius", type=float, required=True, help="Radius of circles to pack")
    parser.add_argument("--output", default="circle_packing.png", help="Output visualization file (.svg or .png)")
    
    args = parser.parse_args()
    
    polygon = read_polygon(args)
    if not polygon:
        print("Error: No polygon provided. Use --input or --poly.")
        sys.exit(1)
        
    print(f"Packing circles of radius {args.radius} into polygon with {len(polygon)} vertices...")
    
    centers = CirclePacker.pack(polygon, args.radius)
    efficiency = CirclePacker.calculate_efficiency(polygon, centers, args.radius)
    
    print(f"\nResults:")
    print(f"  Circles Packed:     {len(centers)}")
    print(f"  Packing Efficiency: {efficiency:.2f}%")
    
    print("\nCircle Centers (First 10):")
    for i, c in enumerate(centers[:10]):
        print(f"  {i+1:2}: ({c.x:.4f}, {c.y:.4f})")
    if len(centers) > 10:
        print(f"  ... and {len(centers)-10} more.")
        
    svg = CirclePacker.visualize(polygon, centers, args.radius)
    
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
