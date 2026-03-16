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

# We need to be careful not to replace the edges_b one which already has it.
# The edges_a one is around line 90.
content = content.replace(old_xor_a, new_xor_a, 1)

# Increase tolerance in _classify_segment
old_classify = '    if poly.point_on_boundary(mid):\n        return "on_boundary"'
new_classify = '    if poly.point_on_boundary(mid) or any(is_on_segment(mid, poly.vertices[i], poly.vertices[(i+1)%len(poly)], tol=1e-6) for i in range(len(poly))):\n        return "on_boundary"'
# Wait, point_on_boundary ALREADY does that loop.
# Let's check point_on_boundary in polygon.py again.
# It uses is_on_segment(point, self.vertices[i], self.vertices[(i + 1) % n])
# which uses the default tol=EPSILON=1e-9.

# So I should change _classify_segment to use a larger tolerance.
old_classify_func = """def _classify_segment(p1: Point2D, p2: Point2D, poly: Polygon) -> str:
    \"\"\"Classify a segment as 'inside', 'outside', or 'on_boundary' of a polygon.\"\"\"
    mid = Point2D((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0)
    
    # Check boundary first as it's more specific
    if poly.point_on_boundary(mid):
        return "on_boundary"
    
    # contains_point handles the 'inside' case
    if poly.contains_point(mid):
        return "inside"
    
    return "outside\"\"\"

# I'll just replace the calls inside _classify_segment
content = content.replace('poly.point_on_boundary(mid)', 'any(is_on_segment(mid, poly.vertices[i], poly.vertices[(i+1)%len(poly)], tol=1e-5) for i in range(len(poly)))')

# Filter slivers
old_recon = '            polygons.append(Polygon(current_poly[:-1]).cleanup())'
new_recon = """            poly = Polygon(current_poly[:-1]).cleanup()
            if poly.area > 1e-4: # Filter out degenerate slivers
                polygons.append(poly)"""
content = content.replace(old_recon, new_recon)

with open(lib_path, 'w') as f:
    f.write(content)

print("Patch v4 applied.")
