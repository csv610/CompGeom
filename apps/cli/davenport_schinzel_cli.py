from __future__ import annotations

import argparse
from compgeom import Point2D
from compgeom import DavenportSchinzel
from compgeom import save_svg, save_png
from ._shared import read_input_lines, parse_points

def parse_segments(lines: list[str]) -> list[tuple[Point2D, Point2D]]:
    segments = []
    for line in lines:
        pts = parse_points([line])
        if len(pts) >= 2:
            segments.append((pts[0], pts[1]))
        else:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    segments.append((Point2D(float(parts[0]), float(parts[1])), 
                                     Point2D(float(parts[2]), float(parts[3]))))
                except ValueError:
                    continue
    return segments

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Calculate Davenport-Schinzel sequence for line segments.")
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--segments", nargs="+", help="Line segments as x1 y1 x2 y2 ...")
    parser.add_argument("--output", help="Output visualization file (.svg or .png)")
    
    args = parser.parse_args(argv)
    
    segments = []
    lines = read_input_lines(args.input)
    if lines:
        segments = parse_segments(lines)
    
    if not segments and args.segments:
        try:
            raw = [float(x) for x in args.segments]
            if len(raw) % 4 != 0:
                print("Error: Each segment needs 4 coordinates (x1 y1 x2 y2).")
                return 1
            for i in range(0, len(raw), 4):
                segments.append((Point2D(raw[i], raw[i+1]), Point2D(raw[i+2], raw[i+3])))
        except ValueError:
            print("Error: Coordinates must be numeric.")
            return 1
            
    if not segments:
        print("Error: No segments provided. Use --segments x1 y1 x2 y2 ... or provide input file.")
        return 1
        
    print(f"Processing {len(segments)} line segments...")
    
    envelope = DavenportSchinzel.lower_envelope_segments(segments)
    sequence = DavenportSchinzel.calculate_sequence(segments)
    
    print("\nLower Envelope Sequence (Segment IDs):")
    print(" -> ".join(map(str, sequence)))
    
    print("\nEnvelope Intervals:")
    for seg in envelope:
        print(f"  ID {seg.segment_id:2}: x from {seg.x_start:6.2f} to {seg.x_end:6.2f} (y = {seg.slope:.2f}x + {seg.intercept:.2f})")

    if args.output:
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
            return height - (padding + (y - min_y) / (max_y - min_y) * (height - 2 * padding)) if max_y > min_y else padding

        svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg.append('<rect width="100%" height="100%" fill="white" />')
        
        for i, (p1, p2) in enumerate(segments):
            svg.append(f'<line x1="{tx(p1.x)}" y1="{ty(p1.y)}" x2="{tx(p2.x)}" y2="{ty(p2.y)}" stroke="#ddd" stroke-width="1" />')
            svg.append(f'<text x="{tx((p1.x+p2.x)/2)}" y="{ty((p1.y+p2.y)/2)}" font-size="10" fill="#999">{i}</text>')
            
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
            
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
