import argparse
import sys
from compgeom.rectangle_packing import RectanglePacker
from compgeom.visualization import save_png, save_svg

def main():
    parser = argparse.ArgumentParser(description="Pack rectangles into minimum area.")
    parser.add_argument("--dims", nargs="+", help="Rectangle dimensions as w1 h1 w2 h2 ...", required=True)
    parser.add_argument("--shape", choices=["rectangle", "square"], default="rectangle", help="Target container shape")
    parser.add_argument("--output", default="packed.png", help="Output visualization file (.svg or .png)")
    parser.add_argument("--cell_size", type=int, default=40, help="Scaling factor for visualization")
    
    args = parser.parse_args()
    
    try:
        raw_dims = [float(x) for x in args.dims]
        if len(raw_dims) % 2 != 0:
            print("Error: Dimensions must be pairs of width and height.")
            sys.exit(1)
            
        dimensions = []
        for i in range(0, len(raw_dims), 2):
            dimensions.append((raw_dims[i], raw_dims[i+1]))
            
    except ValueError:
        print("Error: Dimensions must be numeric.")
        sys.exit(1)
        
    print(f"Packing {len(dimensions)} rectangles into a {args.shape}...")
    
    w, h, placements = RectanglePacker.pack(dimensions, args.shape)
    
    total_rect_area = sum(d[0] * d[1] for d in dimensions)
    container_area = w * h
    efficiency = (total_rect_area / container_area) * 100 if container_area > 0 else 0
    
    print(f"\nContainer Dimensions: {w:.2f} x {h:.2f}")
    print(f"Total Container Area: {container_area:.2f}")
    print(f"Total Rectangles Area: {total_rect_area:.2f}")
    print(f"Packing Efficiency: {efficiency:.2f}%")
    
    print("\nPlacements:")
    for p in sorted(placements, key=lambda x: x.id):
        print(f"  Rect {p.id}: at ({p.x:.2f}, {p.y:.2f}) size {p.width:.2f}x{p.height:.2f}")
        
    svg = RectanglePacker.visualize(w, h, placements, args.cell_size)
    
    if args.output.lower().endswith(".png"):
        try:
            save_png(svg, args.output)
            print(f"\nSaved visualization to {args.output}")
        except RuntimeError as e:
            print(f"\nWarning: Could not generate PNG ({e}). Saving as SVG instead.")
            out_svg = args.output.rsplit('.', 1)[0] + ".svg"
            save_svg(svg, out_svg)
            print(f"Saved visualization to {out_svg}")
    else:
        save_svg(svg, args.output)
        print(f"\nSaved visualization to {args.output}")

if __name__ == "__main__":
    main()
