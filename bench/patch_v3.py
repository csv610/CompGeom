import os

lib_path = "../src/compgeom/polygon/polygon_boolean.py"
os.system(f"git checkout {lib_path}")

with open(lib_path, 'r') as f:
    content = f.read()

# Fix XOR for edges_a ONLY
# We can use the context of 'for p1, p2 in edges_a:'
old_xor_a = """    for p1, p2 in edges_a:
        status = _classify_segment(p1, p2, poly_b_ccw)
        edge_key = (to_key(p1), to_key(p2))
        
        if op == "union":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # For union, keep only one if they have same direction. 
                # If they have opposite direction, both are internal, so drop.
                if edge_key in edges_b_set:
                    kept_edges.append((p1, p2))
        elif op == "intersection":
            if status == "inside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # For intersection, keep if they have same direction.
                if edge_key in edges_b_set:
                    kept_edges.append((p1, p2))
        elif op == "difference":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # If opposite direction, it stays on boundary. If same direction, it's internal.
                if edge_key in edges_b_rev_set:
                     kept_edges.append((p1, p2))
        elif op == "xor":
            if status == "outside":
                kept_edges.append((p1, p2))"""

new_xor_a = """    for p1, p2 in edges_a:
        status = _classify_segment(p1, p2, poly_b_ccw)
        edge_key = (to_key(p1), to_key(p2))
        
        if op == "union":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # For union, keep only one if they have same direction. 
                # If they have opposite direction, both are internal, so drop.
                if edge_key in edges_b_set:
                    kept_edges.append((p1, p2))
        elif op == "intersection":
            if status == "inside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # For intersection, keep if they have same direction.
                if edge_key in edges_b_set:
                    kept_edges.append((p1, p2))
        elif op == "difference":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "on_boundary":
                # If opposite direction, it stays on boundary. If same direction, it's internal.
                if edge_key in edges_b_rev_set:
                     kept_edges.append((p1, p2))
        elif op == "xor":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "inside":
                kept_edges.append((p2, p1))"""

content = content.replace(old_xor_a, new_xor_a)

# Fix verify_boolean_op for union
old_verify_union = '    if op == "union":\n        return area_res <= area_a + area_b + EPSILON'
new_verify_union = '    if op == "union":\n        return max(area_a, area_b) - EPSILON <= area_res <= area_a + area_b + EPSILON'

content = content.replace(old_verify_union, new_verify_union)

# Add sliver filtering in _reconstruct_polygons
old_recon = '            # Remove the last point as it\'s the same as the first\n            polygons.append(Polygon(current_poly[:-1]).cleanup())'
new_recon = """            # Remove the last point as it's the same as the first
            poly = Polygon(current_poly[:-1]).cleanup()
            if poly.area > 1e-4: # Filter out degenerate slivers
                polygons.append(poly)"""

content = content.replace(old_recon, new_recon)

with open(lib_path, 'w') as f:
    f.write(content)

print("Patch applied successfully.")
