import os

lib_path = "../src/compgeom/polygon/polygon_boolean.py"
os.system(f"git checkout {lib_path}")

with open(lib_path, 'r') as f:
    content = f.read()

# Fix XOR for edges_a
old_xor_a = """        elif op == "xor":
            if status == "outside":
                kept_edges.append((p1, p2))"""
new_xor_a = """        elif op == "xor":
            if status == "outside":
                kept_edges.append((p1, p2))
            elif status == "inside":
                kept_edges.append((p2, p1))"""

content = content.replace(old_xor_a, new_xor_a, 1)

# Modify _classify_segment to use larger tolerance for boundary
# We'll use distance_to_point instead of is_on_segment as it's easier to use with tol
old_line = '    if poly.point_on_boundary(mid):'
new_line = '    from ..kernel import dist_point_to_segment\n    if any(dist_point_to_segment(mid, poly.vertices[i], poly.vertices[(i+1)%len(poly)]) < 1e-5 for i in range(len(poly))):'
content = content.replace(old_line, new_line)

# Filter slivers
old_recon = '            # Remove the last point as it\'s the same as the first\n            polygons.append(Polygon(current_poly[:-1]).cleanup())'
new_recon = """            # Remove the last point as it's the same as the first
            poly = Polygon(current_poly[:-1]).cleanup()
            if poly.area > 1e-4: # Filter out degenerate slivers
                polygons.append(poly)"""
content = content.replace(old_recon, new_recon)

with open(lib_path, 'w') as f:
    f.write(content)

print("Patch v6 applied.")
