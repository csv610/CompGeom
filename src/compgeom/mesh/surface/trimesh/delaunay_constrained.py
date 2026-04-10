"""Constrained Delaunay Triangulation (CDT)."""

from __future__ import annotations
from collections import deque
from compgeom.kernel import EPSILON, Point2D, incircle_sign, is_on_segment, orientation_sign


def triangle_area(a: Point2D, b: Point2D, c: Point2D) -> float:
    return abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0)


def _point_key(point: Point2D):
    # Use both coordinates and id to distinguish between identical coordinates if they are different objects
    # But for CDT geometric checks, we often want to treat same-coordinate points as same.
    # However, _splice_hole creates duplicates with same coordinates.
    # To correctly map edges, we must be consistent.
    return (round(point.x / 1e-10), round(point.y / 1e-10), point.id)


def _edge_key(a: Point2D, b: Point2D):
    return tuple(sorted((_point_key(a), _point_key(b))))


def _make_ccw_triangle(a: Point2D, b: Point2D, c: Point2D):
    return (a, b, c) if orientation_sign(a, b, c) >= 0 else (a, c, b)


def _build_edge_map(triangles):
    edge_map = {}
    for triangle_index, triangle in enumerate(triangles):
        for edge in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
            edge_map.setdefault(_edge_key(*edge), []).append(triangle_index)
    return edge_map


def _quadrilateral_for_edge(first, second, shared_edge_key):
    shared_keys = set(shared_edge_key)
    first_opposite = next(vertex for vertex in first if _point_key(vertex) not in shared_keys)
    second_opposite = next(vertex for vertex in second if _point_key(vertex) not in shared_keys)
    shared_vertices = [vertex for vertex in first if _point_key(vertex) in shared_keys]
    a, b = shared_vertices
    return a, b, first_opposite, second_opposite


def _should_flip_constrained_edge(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    """
    Standard Delaunay flip condition: flip edge ab if d is inside circumcircle of abc.
    Assumes abcd is a convex quadrilateral and abc is CCW.
    """
    if orientation_sign(a, b, c) < 0:
        a, b = b, a  # Ensure abc is CCW
        
    return incircle_sign(a, b, c, d) > 0


def _point_on_boundary(point: Point2D, boundary: list[Point2D]) -> bool:
    return any(is_on_segment(point, boundary[index], boundary[(index + 1) % len(boundary)]) for index in range(len(boundary)))


def _proper_segment_intersection(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    o1 = orientation_sign(a, b, c)
    o2 = orientation_sign(a, b, d)
    o3 = orientation_sign(c, d, a)
    o4 = orientation_sign(c, d, b)

    if o1 == 0 and is_on_segment(c, a, b):
        return False
    if o2 == 0 and is_on_segment(d, a, b):
        return False
    if o3 == 0 and is_on_segment(a, c, d):
        return False
    if o4 == 0 and is_on_segment(b, c, d):
        return False
    return o1 != o2 and o3 != o4


def _point_in_domain(point: Point2D, outer_boundary: list[Point2D], holes: list[list[Point2D]]) -> bool:
    from compgeom.polygon.polygon_metrics import is_point_in_polygon
    if not is_point_in_polygon(point, outer_boundary):
        return False
    for hole in holes:
        if is_point_in_polygon(point, hole) and not _point_on_boundary(point, hole):
            return False
    return True


def _segment_valid_in_domain(
    start: Point2D,
    end: Point2D,
    outer_boundary: list[Point2D],
    holes: list[list[Point2D]],
    constrained_segments: set,
) -> bool:
    midpoint = Point2D((start.x + end.x) / 2.0, (start.y + end.y) / 2.0)
    if not _point_in_domain(midpoint, outer_boundary, holes):
        return False

    for boundary in [outer_boundary, *holes]:
        for index, edge_start in enumerate(boundary):
            edge_end = boundary[(index + 1) % len(boundary)]
            if start == edge_start or start == edge_end or end == edge_start or end == edge_end:
                continue
            if _proper_segment_intersection(start, end, edge_start, edge_end):
                return False
    return True


def constrained_delaunay_triangulation(outer_boundary: list[Point2D], holes: list[list[Point2D]] | None = None):
    from compgeom.polygon.polygon import triangulate_polygon_with_holes
    
    holes = holes or []
    triangles, merged_polygon = triangulate_polygon_with_holes(outer_boundary, holes)
    
    # Strictly define all constrained edges: 
    # 1. Outer boundary edges
    # 2. Hole edges
    # 3. Merged polygon edges (including bridge edges between outer and holes)
    constrained_edges = set()
    
    # Add outer boundary edges
    for i in range(len(outer_boundary)):
        constrained_edges.add(_edge_key(outer_boundary[i], outer_boundary[(i + 1) % len(outer_boundary)]))
        
    # Add hole edges
    for hole in holes:
        for i in range(len(hole)):
            constrained_edges.add(_edge_key(hole[i], hole[(i + 1) % len(hole)]))
            
    # Add merged polygon edges (covers bridge edges)
    for i in range(len(merged_polygon)):
        constrained_edges.add(_edge_key(merged_polygon[i], merged_polygon[(i + 1) % len(merged_polygon)]))

    # Use a queue-based approach for efficient edge flipping
    edge_map = _build_edge_map(triangles)
    # Queue of all internal edges (initially all edges that are not constrained)
    queue = deque()
    for ek in edge_map:
        if ek not in constrained_edges:
            queue.append(ek)
    
    # Set to track what's already in the queue to avoid redundant checks
    in_queue = set(queue)
    
    total_flips = 0
    round_limit = len(triangles) * 100 # Reasonable limit
    
    while queue and total_flips < round_limit:
        edge_key = queue.popleft()
        in_queue.remove(edge_key)
        
        owners = edge_map.get(edge_key, [])
        if len(owners) != 2:
            continue

        first_index, second_index = owners
        first = triangles[first_index]
        second = triangles[second_index]
        
        try:
            # a, b are the shared edge vertices. c, d are opposite vertices.
            a, b, c, d = _quadrilateral_for_edge(first, second, edge_key)
        except ValueError:
            continue
        
        # Check if the new edge cd would be valid
        # 1. Quad abcd must be strictly convex
        if orientation_sign(c, d, a) * orientation_sign(c, d, b) >= 0:
            continue
        if orientation_sign(a, b, c) * orientation_sign(a, b, d) >= 0:
            continue
            
        # 2. Check if the flip is needed (Delaunay condition)
        if not _should_flip_constrained_edge(a, b, c, d):
            continue

        # 3. Check if the new edge is valid in the domain (not crossing boundaries/holes)
        if not _segment_valid_in_domain(c, d, outer_boundary, holes, constrained_edges):
            continue

        # Perform the flip ab -> cd
        # New triangles: (c, d, a) and (c, b, d)
        replacement_one = _make_ccw_triangle(c, d, a)
        replacement_two = _make_ccw_triangle(c, b, d)
        
        # Verify that total area is preserved before committing
        area_before = triangle_area(first[0], first[1], first[2]) + triangle_area(second[0], second[1], second[2])
        area_after = triangle_area(replacement_one[0], replacement_one[1], replacement_one[2]) + \
                     triangle_area(replacement_two[0], replacement_two[1], replacement_two[2])
        
        if abs(area_after - area_before) > 1e-7:
            continue

        # Update the triangles
        triangles[first_index] = replacement_one
        triangles[second_index] = replacement_two
        
        # Update the edge_map for the flipped edge
        del edge_map[edge_key]
        new_edge_key = _edge_key(c, d)
        edge_map[new_edge_key] = [first_index, second_index]
        
        # Update edge_map for the four boundary edges of the quad
        # The boundary edges are: (a, c), (a, d), (b, c), (b, d)
        # Their owner triangles might have changed indices or content.
        # Actually, they still belong to first_index or second_index, but we need to re-verify them.
        boundary_edges = [
            (a, c), (a, d), (b, c), (b, d)
        ]
        
        for e_v in boundary_edges:
            ek = _edge_key(*e_v)
            # Find which triangles now own this edge and update edge_map
            owners_ek = []
            for idx, tri in enumerate(triangles):
                # This is inefficient, but let's be correct first. 
                # Optimization: only check first_index, second_index and previous owners.
                pass
            
            # Efficient update of edge owners for boundary edges
            # (a, c) was owned by 'first' or someone else. Now it's owned by replacement_one or someone else.
            # (a, d) was owned by 'second' or someone else. Now it's owned by replacement_one or someone else.
            # (b, c) was owned by 'first' or someone else. Now it's owned by replacement_two or someone else.
            # (b, d) was owned by 'second' or someone else. Now it's owned by replacement_two or someone else.
            
            # Let's just rebuild the edge map locally for these 4 edges.
            if ek in edge_map:
                old_owners = edge_map[ek]
                new_owners = []
                for o_idx in old_owners:
                    if o_idx == first_index or o_idx == second_index:
                        continue # We'll re-add if they still own it
                    new_owners.append(o_idx)
                
                if first_index not in new_owners:
                    tri = triangles[first_index]
                    if ek in [_edge_key(tri[0], tri[1]), _edge_key(tri[1], tri[2]), _edge_key(tri[2], tri[0])]:
                        new_owners.append(first_index)
                if second_index not in new_owners:
                    tri = triangles[second_index]
                    if ek in [_edge_key(tri[0], tri[1]), _edge_key(tri[1], tri[2]), _edge_key(tri[2], tri[0])]:
                        new_owners.append(second_index)
                edge_map[ek] = new_owners

            if ek not in constrained_edges and ek not in in_queue:
                queue.append(ek)
                in_queue.add(ek)
        
        total_flips += 1
        if total_flips % 500 == 0:
            print(f"Flips performed: {total_flips}")

    if total_flips > 0:
        print(f"Total flips: {total_flips}")
        
    return triangles, constrained_edges
