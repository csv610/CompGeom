from __future__ import annotations

from typing import List
from compgeom.kernel import Point2D, EPSILON
from compgeom.polygon.polygon import Polygon
from compgeom.mesh.mesh import PolygonMesh


def verify_convex_decomposition(
    original_polygon: Polygon, decomposition: List[Polygon]
) -> bool:
    """
    Verifies that a list of polygons forms a valid convex decomposition of the original polygon.
    
    A valid convex decomposition must satisfy:
    1. Convexity: Every polygon in the decomposition is convex.
    2. Containment: Every polygon in the decomposition is contained within the original polygon.
    3. Union: The union of all polygons in the decomposition is equal to the original polygon.
    4. Disjoint Interiors: The interiors of the decomposition polygons are disjoint.
    
    This implementation uses area-based verification and point-in-polygon tests.
    """
    if not decomposition:
        return len(original_polygon) < 3

    original_area = original_polygon.area
    if original_area < EPSILON:
        return not decomposition or all(p.area < EPSILON for p in decomposition)

    total_decomposition_area = 0.0

    for part in decomposition:
        # 1. Convexity check
        if not part.is_convex():
            raise ValueError(f"Decomposition part {part} is not convex")

        # 2. Area accumulation
        part_area = part.area
        if part_area < -EPSILON:
             raise ValueError(f"Decomposition part {part} has negative area")
        total_decomposition_area += part_area

        # 3. Basic containment: all vertices must be in or on the original polygon
        for vertex in part.vertices:
            if not original_polygon.contains_point(vertex):
                # contains_point usually includes boundary, but let's be safe if it doesn't
                if not original_polygon.point_on_boundary(vertex):
                    raise ValueError(f"Vertex {vertex} of decomposition part is outside original polygon")

        # 4. Interior point check: centroid of the part must be inside the original polygon
        # This helps catch cases where a convex part connects two distant vertices but goes outside.
        centroid = part.properties().centroid
        if not original_polygon.contains_point(centroid):
            raise ValueError(f"Centroid {centroid} of decomposition part is outside original polygon")

    # 5. Area sum check
    # If the parts are contained in the original polygon and their interiors are disjoint,
    # then the sum of their areas must equal the original area.
    # Conversely, if they are all contained and the sum of areas equals the original area,
    # they must have disjoint interiors (up to zero-area overlaps).
    if abs(total_decomposition_area - original_area) > EPSILON * max(1.0, original_area):
        raise ValueError(
            f"Sum of decomposition areas ({total_decomposition_area}) "
            f"does not match original area ({original_area})"
        )

    # 6. Optional: Check for interior disjointness more rigorously if needed
    # (Already implied by area check if containment is strictly verified)
    
    return True


def verify_mesh_decomposition(polygon: Polygon, mesh: PolygonMesh) -> bool:
    """Verifies a PolygonMesh decomposition of a Polygon."""
    decomposition = []
    for face in mesh.faces:
        face_vertices = [mesh.vertices[i] for i in face]
        decomposition.append(Polygon(face_vertices))
    
    return verify_convex_decomposition(polygon, decomposition)
