import sys
import os

lib_path = "../src/compgeom/polygon/polygon_boolean.py"
with open(lib_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    # Fix XOR for edges_a
    if 'elif op == "xor":' in line and i < 100: # First occurrence (edges_a)
        new_lines.append(line)
        new_lines.append('            if status == "outside":\n')
        new_lines.append('                kept_edges.append((p1, p2))\n')
        new_lines.append('            elif status == "inside":\n')
        new_lines.append('                kept_edges.append((p2, p1))\n')
        continue
    
    # Ignore the original single-line XOR for edges_a if we are on the next line
    if i > 0 and 'elif op == "xor":' in lines[i-1] and 'if status == "outside":' in line and i < 101:
        continue
    if i > 1 and 'elif op == "xor":' in lines[i-2] and 'kept_edges.append((p1, p2))' in line and i < 102:
        continue

    # Filter out tiny polygons in _reconstruct_polygons
    if 'polygons.append(Polygon(current_poly[:-1]).cleanup())' in line:
        new_lines.append('            poly = Polygon(current_poly[:-1]).cleanup()\n')
        new_lines.append('            if poly.area > 1e-6: # Filter out degenerate slivers\n')
        new_lines.append('                polygons.append(poly)\n')
        continue

    new_lines.append(line)

with open(lib_path, 'w') as f:
    f.writelines(new_lines)
print("Patch applied.")
