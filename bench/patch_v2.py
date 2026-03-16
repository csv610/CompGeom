import os

lib_path = "../src/compgeom/polygon/polygon_boolean.py"

# Restore original file first to be sure
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

content = content.replace(old_xor_a, new_xor_a)

# Fix verify_boolean_op for union
old_verify_union = '    if op == "union":\n        return area_res <= area_a + area_b + EPSILON'
new_verify_union = '    if op == "union":\n        return max(area_a, area_b) - EPSILON <= area_res <= area_a + area_b + EPSILON'

content = content.replace(old_verify_union, new_verify_union)

# Add sliver filtering in _reconstruct_polygons
old_recon = '            polygons.append(Polygon(current_poly[:-1]).cleanup())'
new_recon = """            poly = Polygon(current_poly[:-1]).cleanup()
            if poly.area > 1e-6: # Filter out degenerate slivers
                polygons.append(poly)"""

content = content.replace(old_recon, new_recon)

with open(lib_path, 'w') as f:
    f.write(content)

print("Patch applied successfully.")
