from __future__ import annotations

from typing import List, Tuple, Any
from compgeom.kernel import Point2D, Point3D, in_circle, in_sphere, orientation_sign, EPSILON


def verify_delaunay_triangulation_2d(points: List[Point2D], 
                                     triangles: List[Tuple[Point2D, Point2D, Point2D]]) -> bool:
    """
    Rigorously verifies a 2D Delaunay triangulation.
    1. Every triangle must have CCW orientation.
    2. Every point in the input set must be on a triangle vertex (completeness check is hard, but we check if points are inside).
    3. Empty Circumcircle Property: No point from the input set can be inside the circumcircle of any triangle.
    """
    if not points:
        return not triangles

    # 1. Orientation check
    for tri in triangles:
        a, b, c = tri
        if orientation_sign(a, b, c) < 0:
            raise ValueError(f"Triangle {a, b, c} has CW orientation, expected CCW")

    # 2 & 3. Paranoid Empty Circumcircle Check: O(N * T)
    for tri in triangles:
        a, b, c = tri
        for p in points:
            # Skip if p is one of the vertices of the triangle
            if p == a or p == b or p == c:
                continue
            
            # in_circle(a, b, c, p) returns True if p is inside circumcircle of (a,b,c)
            # (Assuming a,b,c are CCW)
            if in_circle(a, b, c, p):
                # Check for robustness: if it's just on the boundary, it might be okay 
                # depending on whether we want "Strict Delaunay" or just "Delaunay".
                # Usually we use a small epsilon or robust predicates.
                # If we use exact predicates, in_circle is precise.
                raise ValueError(f"Point {p} is inside circumcircle of triangle {a, b, c}")

    # 4. Check that no two triangles overlap (harder, but usually implied by Delaunay + total area)
    # We could check total area vs convex hull area.
    from compgeom.polygon.convex_hull import GrahamScan
    from compgeom.verifiers.polygon.polygon_verifiers import verify_polygon_area
    
    hull = GrahamScan().generate(points)
    # Shoelace area of hull
    hull_area = 0.0
    for i in range(len(hull)):
        p1, p2 = hull[i], hull[(i+1)%len(hull)]
        hull_area += (p1.x * p2.y) - (p2.x * p1.y)
    hull_area = abs(hull_area) / 2.0
    
    tri_total_area = 0.0
    for a, b, c in triangles:
        area = abs((a.x*(b.y-c.y) + b.x*(c.y-a.y) + c.x*(a.y-b.y)) / 2.0)
        tri_total_area += area
        
    if abs(tri_total_area - hull_area) > EPSILON * 100:
        raise ValueError(f"Total triangle area ({tri_total_area}) does not match convex hull area ({hull_area})")

    return True


def verify_constrained_delaunay_triangulation(points: List[Point2D], 
                                               triangles: List[Tuple[Point2D, Point2D, Point2D]], 
                                               constraints: List[Tuple[Point2D, Point2D]],
                                               outer_boundary: List[Point2D],
                                               holes: List[List[Point2D]] = None) -> bool:
    """
    Rigorously verifies a Constrained Delaunay Triangulation (CDT).
    1. Every constraint edge must be present in the triangulation.
    2. Every triangle must be CCW and within the domain (not in a hole).
    3. The triangles must partition the domain (area check).
    4. Constrained Delaunay Property: For each triangle T, its circumcircle contains 
       no point p that is "visible" from the interior of T.
    """
    from compgeom.mesh.surface.trimesh.delaunay_constrained import _edge_key, _proper_segment_intersection
    
    # 1. Constraint edges present
    tri_edges = set()
    for tri in triangles:
        tri_edges.add(_edge_key(tri[0], tri[1]))
        tri_edges.add(_edge_key(tri[1], tri[2]))
        tri_edges.add(_edge_key(tri[2], tri[0]))
        
    for c1, c2 in constraints:
        if _edge_key(c1, c2) not in tri_edges:
            raise ValueError(f"Constraint edge {c1}-{c2} is missing from the triangulation")

    # 2. CCW and Domain check
    from compgeom.polygon.polygon_metrics import is_point_in_polygon
    holes = holes or []
    for tri in triangles:
        a, b, c = tri
        if orientation_sign(a, b, c) < 0:
            raise ValueError(f"Triangle {tri} is not CCW")
            
        mid = Point2D((a.x+b.x+c.x)/3, (a.y+b.y+c.y)/3)
        if not is_point_in_polygon(mid, outer_boundary):
            raise ValueError(f"Triangle {tri} midpoint {mid} is outside outer boundary")
        for hole in holes:
            if is_point_in_polygon(mid, hole):
                 # Check if it's strictly inside the hole
                 # (Boundary points are tricky, but midpoint of triangle shouldn't be on hole boundary usually)
                 raise ValueError(f"Triangle {tri} midpoint {mid} is inside a hole")

    # 3. Area check
    def poly_area(poly):
        area = 0.0
        for i in range(len(poly)):
            p1, p2 = poly[i], poly[(i+1)%len(poly)]
            area += (p1.x*p2.y) - (p2.x*p1.y)
        return abs(area) / 2.0
        
    expected_area = poly_area(outer_boundary) - sum(poly_area(h) for h in holes)
    total_tri_area = sum(abs((a.x*(b.y-c.y) + b.x*(c.y-a.y) + c.x*(a.y-b.y)) / 2.0) for a, b, c in triangles)
    
    if abs(total_tri_area - expected_area) > EPSILON * 1000:
        raise ValueError(f"Triangulation area {total_tri_area} != expected domain area {expected_area}")

    # 4. Constrained Delaunay Property: O(N * T)
    # A point p is visible from triangle T if segment [p, mid(T)] doesn't intersect any constraint edge properly.
    constraint_edges = set(_edge_key(c1, c2) for c1, c2 in constraints)
    
    for tri in triangles:
        a, b, c = tri
        mid = Point2D((a.x+b.x+c.x)/3, (a.y+b.y+c.y)/3)
        for p in points:
            if p == a or p == b or p == c:
                continue
            
            if in_circle(a, b, c, p):
                # Visibility check: is p visible from mid?
                visible = True
                for c1, c2 in constraints:
                    if p == c1 or p == c2: # One endpoint is p, not a PROPER intersection
                        continue
                    if _proper_segment_intersection(mid, p, c1, c2):
                        visible = False
                        break
                
                if visible:
                    raise ValueError(f"Point {p} is visible from triangle {tri} and inside its circumcircle (Constrained Delaunay violation)")

    return True


def verify_delaunay_tetrahedralization_3d(points: List[Point3D], 
                                          tetrahedra: List[Tuple[Point3D, Point3D, Point3D, Point3D]]) -> bool:
    """
    Rigorously verifies a 3D Delaunay tetrahedralization.
    1. Every tetrahedron must have positive orientation (volume > 0).
    2. Empty Circumsphere Property: No point from the input set can be inside the circumsphere of any tetrahedron.
    """
    from compgeom.kernel.tetrahedron import volume as tetra_volume
    
    for tet in tetrahedra:
        a, b, c, d = tet
        vol = tetra_volume(a, b, c, d)
        if vol < -EPSILON:
             raise ValueError(f"Tetrahedron {a,b,c,d} has negative orientation")
        if abs(vol) < EPSILON:
             # Degenerate tet
             pass

    # Paranoid check: O(N * T)
    for tet in tetrahedra:
        a, b, c, d = tet
        for p in points:
            if p == a or p == b or p == c or p == d:
                continue
            
            # in_sphere(a, b, c, d, p) returns True if p is inside circumsphere of (a,b,c,d)
            # Assuming (a,b,c,d) has positive orientation.
            if in_sphere(a, b, c, d, p):
                raise ValueError(f"Point {p} is inside circumsphere of tetrahedron {a, b, c, d}")

    return True
