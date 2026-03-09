import argparse
import sys
from compgeom.polygon import PolygonGenerator
from compgeom.visualization import save_png, save_svg

def main():
    parser = argparse.ArgumentParser(description="Generate random polygons.")
    parser.add_argument("type", choices=["convex", "concave", "star"], help="Type of polygon to generate")
    parser.add_argument("--n", type=int, default=15, help="Number of vertices")
    parser.add_argument("--output", default="generated_polygon.png", help="Output visualization file")
    
    args = parser.parse_args()
    
    print(f"Generating random {args.type} polygon with {args.n} vertices...")
    
    if args.type == "convex":
        poly = PolygonGenerator.convex(args.n)
    elif args.type == "concave":
        poly = PolygonGenerator.concave(args.n)
    else:
        poly = PolygonGenerator.star_shaped(args.n)
        
    print(f"Result: Polygon with {len(poly)} vertices.")

    # Visualize
    def poly_to_svg(p_list, width=800, height=600):
        all_pts = []
        for p in p_list: all_pts.extend([p.x, p.y])
        min_x, max_x = min(all_pts[0::2]), max(all_pts[0::2])
        min_y, max_y = min(all_pts[1::2]), max(all_pts[1::2])
        
        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="#f8f9fa" />')
        
        def tx(x): return 50 + (x - min_x) / (max_x - min_x) * (width - 100) if max_x > min_x else 50
        def ty(y): return height - (50 + (y - min_y) / (max_y - min_y) * (height - 100)) if max_y > min_y else 50
        
        pts_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in p_list)
        svg.append(f'<polygon points="{pts_str}" fill="white" stroke="black" stroke-width="2" />')
        for p in p_list:
            svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="3" fill="red" />')
            
        svg.append('</svg>')
        return "\n".join(svg)

    svg_content = poly_to_svg(poly)
    
    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"Saved visualization to {args.output}")
        except Exception:
            save_svg(svg_content, args.output.rsplit('.', 1)[0] + ".svg")
    else:
        save_svg(svg_content, args.output)

if __name__ == "__main__":
    main()
