"""Topology and Delaunay property verification for triangular meshes."""

from __future__ import annotations
from compgeom.kernel import Point2D, in_circle, cross_product


class MeshTriangle:
    """A triangle in a mesh with connectivity information."""
    def __init__(self, v1: Point2D, v2: Point2D, v3: Point2D):
        # Ensure CCW orientation
        self.vertices = [v1, v2, v3] if cross_product(v1, v2, v3) >= 0 else [v1, v3, v2]
        self.neighbors: list[MeshTriangle | None] = [None, None, None]

    def get_edge(self, index: int) -> tuple[int, int]:
        """Returns the IDs of the vertices forming the edge opposite to the vertex at index."""
        v1 = self.vertices[(index + 1) % 3]
        v2 = self.vertices[(index + 2) % 3]
        return tuple(sorted((v1.id, v2.id)))

    def find_neighbor_index(self, other: MeshTriangle) -> int:
        """Returns the index of the neighbor triangle."""
        for index, neighbor in enumerate(self.neighbors):
            if neighbor == other:
                return index
        return -1


def build_topology(triangles: list[tuple[Point2D, Point2D, Point2D]]) -> list[MeshTriangle]:
    """Builds a mesh with neighborhood information from a list of triangles."""
    mesh = [MeshTriangle(*triangle) for triangle in triangles]
    edge_map = {}
    for triangle_index, triangle in enumerate(mesh):
        for edge_index in range(3):
            edge = triangle.get_edge(edge_index)
            if edge not in edge_map:
                edge_map[edge] = (triangle_index, edge_index)
                continue
            other_triangle_index, other_edge_index = edge_map[edge]
            triangle.neighbors[edge_index] = mesh[other_triangle_index]
            mesh[other_triangle_index].neighbors[other_edge_index] = triangle
    return mesh


def is_delaunay(mesh: list[MeshTriangle]) -> bool:
    """Checks if the mesh satisfies the Delaunay property."""
    for t1 in mesh:
        for i1, t2 in enumerate(t1.neighbors):
            if t2 is None:
                continue

            i2 = t2.find_neighbor_index(t1)
            a = t1.vertices[i1]
            b = t1.vertices[(i1 + 1) % 3]
            c = t1.vertices[(i1 + 2) % 3]
            d = t2.vertices[i2]

            if in_circle(a, b, c, d):
                return False
    return True


def get_nondelaunay_triangles(mesh: list[MeshTriangle]) -> set[MeshTriangle]:
    """Returns the set of triangles that violate the Delaunay property."""
    bad_triangles = set()
    for t1 in mesh:
        for i1, t2 in enumerate(t1.neighbors):
            if t2 is None:
                continue

            i2 = t2.find_neighbor_index(t1)
            a = t1.vertices[i1]
            b = t1.vertices[(i1 + 1) % 3]
            c = t1.vertices[(i1 + 2) % 3]
            d = t2.vertices[i2]

            if in_circle(a, b, c, d):
                bad_triangles.add(t1)
                bad_triangles.add(t2)
    return bad_triangles
