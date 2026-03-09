import argparse
import sys
from compgeom.geometry import Point
from compgeom.polygon import generate_simple_polygon
from compgeom.polygon_smoothing import PolygonalMeanCurvatureFlow
from compgeom.visualization import save_png, save_svg

def main():
    parser = argparse.ArgumentParser(description="Smooth a polygon using Mean Curvature Flow.")
    parser.add_argument("--poly", nargs="+", help="Polygon vertices as x1 y1 x2 y2 ...")
    parser.add_argument("--n_points", type=int, default=50, help="Number of points for uniform resampling")
    parser.add_argument("--iterations", type=int, default=100, help="Number of smoothing iterations")
    parser.add_argument("--dt", type=float, default=0.1, help="Time step for the flow")
    parser.add_argument("--output", default="smoothed_polygon.png", help="Output visualization file")
    
    args = parser.parse_args()
    
    if args.poly:
        try:
            raw = [float(x) for x in args.poly]
            polygon = [Point(raw[i], raw[i+1], i//2) for i in range(0, len(raw), 2)]
        except (ValueError, IndexError):
            print("Error: Invalid polygon coordinates.")
            sys.exit(1)
    else:
        print("Generating random simple polygon...")
        polygon = generate_simple_polygon(n_points=20, x_range=(10, 90), y_range=(10, 90))
        
    print(f"Initial Polygon: {len(polygon)} vertices.")
    
    # 1. Resample
    print(f"Resampling to {args.n_points} uniform segments...")
    resampled = PolygonalMeanCurvatureFlow.resample_polygon(polygon, args.n_points)
    
    # 2. Smooth
    print(f"Applying MCF for {args.iterations} iterations (dt={args.dt})...")
    smoothed = PolygonalMeanCurvatureFlow.smooth(resampled, args.iterations, args.dt, keep_perimeter=True)
    
    print("Done.")
    
    # 3. Visualize
    def poly_to_svg(poly_list, width=800, height=600):
        # Scale to fit
        all_pts = []
        for p in poly_list: all_pts.extend([p.x, p.y])
        min_x, max_x = min(all_pts), max(all_pts)
        min_y, max_y = min(all_pts[1::2]), max(all_pts[1::2])
        
        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="white" />')
        
        def tx(x): return 50 + (x - min_x) / (max_x - min_x) * (width - 100) if max_x > min_x else 50
        def ty(y): return height - (50 + (y - min_y) / (max_y - min_y) * (height - 100)) if max_y > min_y else 50
        
        # Original (dashed)
        orig_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in polygon)
        svg.append(f'<polygon points="{orig_str}" fill="none" stroke="#ddd" stroke-dasharray="5,5" />')
        
        # Smoothed
        smooth_str = " ".join(f"{tx(p.x)},{ty(p.y)}" for p in smoothed)
        svg.append(f'<polygon points="{smooth_str}" fill="none" stroke="red" stroke-width="3" />')
        
        svg.append('</svg>')
        return "\n".join(svg)

    svg_content = poly_to_svg(smoothed)
    
    if args.output.lower().endswith(".png"):
        try:
            save_png(svg_content, args.output)
            print(f"Saved visualization to {args.output}")
        except Exception as e:
            save_svg(svg_content, args.output.rsplit('.', 1)[0] + ".svg")
    else:
        save_svg(svg_content, args.output)

if __name__ == "__main__":
    main()
