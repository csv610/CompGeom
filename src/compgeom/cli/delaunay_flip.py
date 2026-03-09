import sys
from compgeom.geometry import Point
from compgeom.triangulation import build_topology, delaunay_flip

def main():
    points_map, triangles_data, reading_points = {}, [], True
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        parts = line.split()
        if parts[0].upper() == 'T': reading_points = False; continue
        if reading_points:
            try:
                if len(parts) >= 3:
                    pid = int(parts[0]); x, y = float(parts[1]), float(parts[2])
                    points_map[pid] = Point(x, y, pid)
                elif len(parts) == 2:
                    pid = len(points_map); x, y = float(parts[0]), float(parts[1])
                    points_map[pid] = Point(x, y, pid)
            except ValueError: reading_points = False
        if not reading_points:
            try:
                if len(parts) >= 3:
                    p_ids = [int(x) for x in parts[:3]]
                    triangles_data.append([points_map[pid] for pid in p_ids])
            except (ValueError, KeyError): continue
    if not triangles_data:
        print("No triangles found in input."); return
    mesh = build_topology(triangles_data)
    delaunay_flip(mesh)
    print(f"Delaunay Triangulation: {len(mesh)} triangles.")
    for i, tri in enumerate(mesh):
        ids = sorted([v.id for v in tri.vertices])
        print(f"Triangle {i:3}: {ids[0]:3}, {ids[1]:3}, {ids[2]:3}")

if __name__ == "__main__":
    main()
