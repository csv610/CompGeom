import os

lib_path = "../src/compgeom/polygon/polygon_boolean.py"
os.system(f"git checkout {lib_path}")

with open(lib_path, 'r') as f:
    content = f.read()

# Fix XOR for edges_a (first occurrence only)
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
old_line = '    if poly.point_on_boundary(mid):'
new_line = '    if any(is_on_segment(mid, poly.vertices[i], poly.vertices[(i+1)%len(poly)], tol=1e-5) for i in range(len(poly))):'
content = content.replace(old_line, new_line)

# Filter slivers
old_recon = '            polygons.append(Polygon(current_poly[:-1]).cleanup())'
new_recon = """            poly = Polygon(current_poly[:-1]).cleanup()
            if poly.area > 1e-4: # Filter out degenerate slivers
                polygons.append(poly)"""
content = content.replace(old_recon, new_recon)

with open(lib_path, 'w') as f:
    f.write(content)

print("Patch v5 applied.")
