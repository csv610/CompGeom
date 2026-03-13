import argparse
import sys
from compgeom import Point2D
from compgeom import get_reflex_vertices, generate_simple_polygon
from compgeom import OBJFileHandler
from compgeom import save_png, save_svg

def read_polygon(args):
    if args.input:
        print(f"Reading polygon from {args.input}...")
        vertices, _ = OBJFileHandler.read(args.input)
        return [Point2D(v.x, v.y) for v in vertices]
    
    if args.poly:
        try:
            raw = [float(x) for x in args.poly]
            return [Point2D(raw[i], raw[i+1], i//2) for i in range(0, len(raw), 2)]
        except (ValueError, IndexError):
            print("Error: Invalid polygon coordinates.")
            sys.exit(1)
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Identify vertices forming concave parts of a polygon.")
    parser.add_argument("--input", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--output", default="concave_parts.png", help="Output visualization file")
    
    args = parser.parse_args()
    
    polygon = read_polygon(args)
    if not polygon:
        print("Generating random simple polygon...")
        polygon = generate_simple_polygon(n_points=15, x_range=(10, 90), y_range=(10, 90))
        
    print(f"Initial Polygon: {len(polygon)} vertices.")
    
    reflex_vertices = get_reflex_vertices(polygon)
    
    print(f"\nFound {len(reflex_vertices)} reflex (concave) vertices.")
    for i, v in enumerate(reflex_vertices):
        print(f"  {i+1}: {v}")

    # Visualize
    def poly_to_svg(poly, concave_pts, width=800, height=600):
        all_pts = []
        for p in poly: all_pts.extend([p.x, p.y])
        min_x, max_x = min(all_pts[0::2]), max(all_pts[0::2])
        min_y, max_y = min(all_pts[1::2]), max(all_pts[1::2])
        
        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="#f8f9fa" />')
        
        def tx(x): return 50 + (x - min_x) / (max_x - min_x) * (width - 100) if max_x > min_x else 50
        def ty(y): return height - (50 + (y - min_y) / (max_y - min_y) * (height - 100)) if max_y > min_y else 50
        
        pts_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in poly)
        svg.append(f'<polygon points="{pts_str}" fill="white" stroke="black" stroke-width="2" />')
        
        for p in poly:
            svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="3" fill="#ccc" />')
            
        for p in concave_pts:
            svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="6" fill="red" />')
            svg.append(f'<circle cx="{tx(p.x)}" cy="{ty(p.y)}" r="8" fill="none" stroke="red" stroke-width="1" />')
            
        svg.append('</svg>')
        return "\n".join(svg)

    svg_content = poly_to_svg(polygon, reflex_vertices)
    
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
