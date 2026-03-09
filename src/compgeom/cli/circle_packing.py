import argparse
import sys
from compgeom.geometry import Point
from compgeom.polygon import CirclePacker
from compgeom.visualization import save_png, save_svg

def main():
    parser = argparse.ArgumentParser(description="Pack circles into a closed polygon.")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...", required=True)
    parser.add_argument("--radius", type=float, required=True, help="Radius of circles to pack")
    parser.add_argument("--output", default="circle_packing.png", help="Output visualization file (.svg or .png)")
    
    args = parser.parse_args()
    
    try:
        raw = [float(x) for x in args.poly]
        if len(raw) % 2 != 0:
            print("Error: Polygon needs pairs of coordinates (x1 y1).")
            sys.exit(1)
            
        polygon = []
        for i in range(0, len(raw), 2):
            polygon.append(Point(raw[i], raw[i+1]))
            
    except ValueError:
        print("Error: Coordinates must be numeric.")
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
