import argparse
import sys
from compgeom import Point
from compgeom import DavenportSchinzel
from compgeom import save_svg, save_png

def main():
    parser = argparse.ArgumentParser(description="Calculate Davenport-Schinzel sequence for line segments.")
    parser.add_argument("--segments", nargs="+", help="Line segments as x1 y1 x2 y2 ...", required=True)
    parser.add_argument("--output", help="Output visualization file (.svg or .png)")
    
    args = parser.parse_args()
    
    try:
        raw = [float(x) for x in args.segments]
        if len(raw) % 4 != 0:
            print("Error: Each segment needs 4 coordinates (x1 y1 x2 y2).")
            sys.exit(1)
            
        segments = []
        for i in range(0, len(raw), 4):
            segments.append((Point(raw[i], raw[i+1]), Point(raw[i+2], raw[i+3])))
            
    except ValueError:
        print("Error: Coordinates must be numeric.")
        sys.exit(1)
        
    print(f"Processing {len(segments)} line segments...")
    
    envelope = DavenportSchinzel.lower_envelope_segments(segments)
    sequence = DavenportSchinzel.calculate_sequence(segments)
    
    print("\nLower Envelope Sequence (Segment IDs):")
    print(" -> ".join(map(str, sequence)))
    
    print("\nEnvelope Intervals:")
    for seg in envelope:
        print(f"  ID {seg.segment_id:2}: x from {seg.x_start:6.2f} to {seg.x_end:6.2f} (y = {seg.slope:.2f}x + {seg.intercept:.2f})")

    if args.output:
        # Simple SVG visualization for the envelope
        all_x = []
        all_y = []
        for p1, p2 in segments:
            all_x.extend([p1.x, p2.x])
            all_y.extend([p1.y, p2.y])
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        width = 800
        height = 400
        padding = 40
        
        def tx(x):
            return padding + (x - min_x) / (max_x - min_x) * (width - 2 * padding) if max_x > min_x else padding
        
        def ty(y):
            # Invert Y for SVG
            return height - (padding + (y - min_y) / (max_y - min_y) * (height - 2 * padding)) if max_y > min_y else padding

        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="white" />')
        
        # Draw original segments in light gray
        for i, (p1, p2) in enumerate(segments):
            svg.append(f'<line x1="{tx(p1.x)}" y1="{ty(p1.y)}" x2="{tx(p2.x)}" y2="{ty(p2.y)}" stroke="#ddd" stroke-width="1" />')
            svg.append(f'<text x="{tx((p1.x+p2.x)/2)}" y="{ty((p1.y+p2.y)/2)}" font-size="10" fill="#999">{i}</text>')
            
        # Draw lower envelope in red
        for seg in envelope:
            y_start = seg.y_at(seg.x_start)
            y_end = seg.y_at(seg.x_end)
            svg.append(f'<line x1="{tx(seg.x_start)}" y1="{ty(y_start)}" x2="{tx(seg.x_end)}" y2="{ty(y_end)}" stroke="red" stroke-width="3" />')
            
        svg.append('</svg>')
        svg_content = "\n".join(svg)
        
        if args.output.lower().endswith(".png"):
            try:
                save_png(svg_content, args.output)
                print(f"\nSaved visualization to {args.output}")
            except Exception as e:
                print(f"\nWarning: Could not save PNG ({e}). Saving as SVG.")
                save_svg(svg_content, args.output.rsplit('.', 1)[0] + ".svg")
        else:
            save_svg(svg_content, args.output)
            print(f"\nSaved visualization to {args.output}")

if __name__ == "__main__":
    main()
