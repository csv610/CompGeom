import argparse
import sys
from compgeom import Point
from compgeom import generate_simple_polygon, PolygonalMeanCurvatureFlow
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
    parser = argparse.ArgumentParser(description="Smooth a polygon using Mean Curvature Flow.")
    parser.add_argument("--input", help="Path to input OBJ file defining the polygon")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--n_points", type=int, default=50, help="Number of points for uniform resampling")
    parser.add_argument("--iterations", type=int, default=100, help="Number of smoothing iterations")
    parser.add_argument("--dt", type=float, default=0.1, help="Time step for the flow")
    parser.add_argument("--no_center", action="store_false", dest="fix_centroid", help="Do not fix centroid at (0,0)")
    parser.add_argument("--output", default="smoothed_polygon.png", help="Output visualization file")
    
    args = parser.parse_args()
    fix_centroid = getattr(args, 'fix_centroid', True)
    
    polygon = read_polygon(args)
    if not polygon:
        print("Generating random simple polygon...")
        polygon = generate_simple_polygon(n_points=20, x_range=(10, 90), y_range=(10, 90))
        
    print(f"Initial Polygon: {len(polygon)} vertices.")
    
    # 1. Resample
    print(f"Resampling to {args.n_points} uniform segments...")
    resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, args.n_points)
    
    # 2. Smooth
    print(f"Applying MCF for {args.iterations} iterations (dt={args.dt})...")
    if fix_centroid:
        print("Constraint: Centroid is fixed at (0,0).")
        
    smoothed = PolygonalMeanCurvatureFlow.smooth(
        resampled, 
        args.iterations, 
        args.dt, 
        keep_perimeter=True, 
        fix_centroid=fix_centroid
    )
    
    print("Done.")
    
    # 3. Visualize
    def poly_to_svg(poly_list, width=800, height=600):
        all_pts = []
        for p in poly_list: all_pts.extend([p.x, p.y])
        if polygon:
            for p in polygon: all_pts.extend([p.x, p.y])
            
        max_coord = max(max(abs(x) for x in all_pts), 1.0) * 1.2
        
        svg = [f'<svg width="{width}" height="{height}" viewBox="{-max_coord} {-max_coord} {2*max_coord} {2*max_coord}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect x="-100%" y="-100%" width="200%" height="200%" fill="white" />')
        svg.append(f'<line x1="{-max_coord}" y1="0" x2="{max_coord}" y2="0" stroke="#eee" stroke-width="0.5" />')
        svg.append(f'<line x1="0" y1="{-max_coord}" x2="0" y2="{max_coord}" stroke="#eee" stroke-width="0.5" />')
        
        # Center original for comparison
        cx = sum(p.x for p in polygon) / len(polygon)
        cy = sum(p.y for p in polygon) / len(polygon)
        centered_orig = [Point(p.x - cx, p.y - cy) for p in polygon]

        def to_pts(pts): return " ".join(f"{p.x},{-p.y}" for p in pts) 
        
        svg.append(f'<polygon points="{to_pts(centered_orig)}" fill="none" stroke="#ddd" stroke-dasharray="2,2" />')
        svg.append(f'<polygon points="{to_pts(smoothed)}" fill="none" stroke="red" stroke-width="2" />')
        svg.append('<circle cx="0" cy="0" r="2" fill="blue" />')
        svg.append('</svg>')
        return "\n".join(svg)

    svg_content = poly_to_svg(smoothed)
    
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
