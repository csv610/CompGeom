from __future__ import annotations

import argparse
from _shared import read_input_lines, parse_points, visualize_with_pyvista
from compgeom.mesh.surface.trimesh.delaunay_constrained import constrained_delaunay_triangulation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute Constrained Delaunay Triangulation for a polygon with optional holes."
    )
    parser.add_argument("input", nargs="?", help="Path to input file (optional, reads from stdin if omitted).")
    parser.add_argument("--visualize", action="store_true", help="Visualize the CDT using pyvista.")
    args = parser.parse_args(argv)

    lines = read_input_lines(args.input)
    if not lines:
        print("Error: No input polygon provided. Provide outer boundary, then 'HOLE' for each hole.")
        return 1
        
    outer_boundary_lines = []
    holes_data = []
    current_hole = []
    mode = "outer"
    
    for line in lines:
        if line.strip().upper() == "HOLE":
            if current_hole:
                holes_data.append(current_hole)
            current_hole = []
            mode = "hole"
            continue
        if mode == "outer":
            outer_boundary_lines.append(line)
        else:
            current_hole.append(line)
            
    if current_hole:
        holes_data.append(current_hole)

    outer_boundary = parse_points(outer_boundary_lines)
    if len(outer_boundary) < 3:
        print("Error: Outer boundary must have at least 3 vertices.")
        return 1
        
    holes = [parse_points(h) for h in holes_data]
    holes = [h for h in holes if len(h) >= 3]

    print(f"Computing CDT for polygon with {len(outer_boundary)} vertices and {len(holes)} holes...")
    triangles, _ = constrained_delaunay_triangulation(outer_boundary, holes)
    
    print(f"Triangulation complete: {len(triangles)} triangles.")
    for i, (a, b, c) in enumerate(triangles):
        print(f"Triangle {i:3}: ({a.x:.4f}, {a.y:.4f}), ({b.x:.4f}, {b.y:.4f}), ({c.x:.4f}, {c.y:.4f})")
        
    if args.visualize:
        # Collect all points for pyvista
        all_pts = list(outer_boundary)
        for h in holes:
            all_pts.extend(h)
            
        point_to_idx = {p: i for i, p in enumerate(all_pts)}
        faces = []
        for a, b, c in triangles:
            # Note: triangles from CDT might use points not in the original list if they were duplicated or cleaned
            # But CDT usually returns the same Point2D instances. 
            # To be safe, we rebuild the point list if needed, but here we assume original instances.
            try:
                faces.append([point_to_idx[a], point_to_idx[b], point_to_idx[c]])
            except KeyError:
                # If CDT created new point instances (unlikely with current implementation)
                pass
                
        visualize_with_pyvista(points=all_pts, faces=faces)
        
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
