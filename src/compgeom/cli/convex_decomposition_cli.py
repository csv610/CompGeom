import argparse
import sys
from compgeom import Point
from compgeom import PolygonDecomposer, generate_simple_polygon
from compgeom import OBJFileHandler
from compgeom import save_png, save_svg

def read_polygon(args):
    if args.input:
        print(f"Reading polygon from {args.input}...")
        vertices, _ = OBJFileHandler.read(args.input)
        return [Point(v.x, v.y) for v in vertices]
    
    if args.poly:
        try:
            raw = [float(x) for x in args.poly]
            return [Point(raw[i], raw[i+1], i//2) for i in range(0, len(raw), 2)]
        except (ValueError, IndexError):
            print("Error: Invalid polygon coordinates.")
            sys.exit(1)
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Decompose a polygon into convex pieces using Hertel-Mehlhorn.")
    parser.add_argument("--input", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--output", default="convex_decomposition.png", help="Output visualization file")
    
    args = parser.parse_args()
    
    polygon = read_polygon(args)
    if not polygon:
        print("Generating random simple polygon...")
        polygon = generate_simple_polygon(n_points=15, x_range=(10, 90), y_range=(10, 90))
        
    print(f"Initial Polygon: {len(polygon)} vertices.")
    
    # Decompose
    mesh = PolygonDecomposer.convex_decomposition(polygon)
    pieces = [[mesh.vertices[index] for index in face] for face in mesh.faces]
    
    print(f"\nDecomposed into {len(pieces)} convex pieces.")
    for i, piece in enumerate(pieces):
        print(f"  Piece {i+1}: {len(piece)} vertices")

    # Visualize
    def pieces_to_svg(poly_pieces, width=800, height=600):
        all_pts = []
        for piece in poly_pieces:
            for p in piece:
                all_pts.extend([p.x, p.y])
        
        min_x, max_x = min(all_pts[0::2]), max(all_pts[0::2])
        min_y, max_y = min(all_pts[1::2]), max(all_pts[1::2])
        
        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="#f8f9fa" />')
        
        def tx(x): return 50 + (x - min_x) / (max_x - min_x) * (width - 100) if max_x > min_x else 50
        def ty(y): return height - (50 + (y - min_y) / (max_y - min_y) * (height - 100)) if max_y > min_y else 50
        
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#1abc9c", "#e67e22"]
        
        for i, piece in enumerate(poly_pieces):
            pts_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in piece)
            color = colors[i % len(colors)]
            svg.append(f'<polygon points="{pts_str}" fill="{color}" fill-opacity="0.5" stroke="black" stroke-width="1" />')
            
            cx = sum(p.x for p in piece) / len(piece)
            cy = sum(p.y for p in piece) / len(piece)
            svg.append(f'<text x="{tx(cx)}" y="{ty(cy)}" font-size="12" text-anchor="middle" fill="black">{i+1}</text>')
            
        svg.append('</svg>')
        return "\n".join(svg)

    svg_content = pieces_to_svg(pieces)
    
    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"\nSaved visualization to {args.output}")
        except Exception:
            save_svg(svg_content, args.output.rsplit('.', 1)[0] + ".svg")
    else:
        save_svg(svg_content, args.output)

if __name__ == "__main__":
    main()
