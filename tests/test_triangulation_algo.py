import unittest
from compgeom.kernel import Point2D, incircle_sign
from compgeom.mesh import triangulate, constrained_delaunay_triangulation

class TriangulationTests(unittest.TestCase):
    def test_square_triangulates_into_two_faces(self):
        points = [Point2D(0, 0, 0), Point2D(1, 0, 1), Point2D(0, 1, 2), Point2D(1, 1, 3)]
        mesh = triangulate(points)
        skipped = getattr(mesh, 'skipped_points', [])
        self.assertEqual(len(skipped), 0)
        self.assertEqual(len(mesh.faces), 2)
        
        # Convert faces back to point tuples if needed for the test, or test faces directly
        triangles = [(mesh.vertices[f[0]], mesh.vertices[f[1]], mesh.vertices[f[2]]) for f in mesh.faces]
        vertex_ids = sorted(sorted(vertex.id for vertex in triangle) for triangle in triangles)
        self.assertIn(vertex_ids, [[[0, 1, 2], [1, 2, 3]], [[0, 1, 3], [0, 2, 3]]])

    def test_constrained_delaunay_preserves_domain_edges_and_area(self):
        outer = [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)]
        holes = [[Point2D(2, 2), Point2D(4, 2), Point2D(4, 4), Point2D(2, 4)]]
        triangles, constrained_edges = constrained_delaunay_triangulation(outer, holes)
        self.assertEqual(len(triangles), 8)
        self.assertGreaterEqual(len(constrained_edges), 8)

        covered_area = 0.0
        for a, b, c in triangles:
            covered_area += abs(
                (a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2.0
            )
        self.assertAlmostEqual(covered_area, 32.0, places=6)

    def test_constrained_delaunay_is_locally_delaunay_on_unconstrained_edges(self):
        outer = [Point2D(0, 0), Point2D(5, 0), Point2D(5, 5), Point2D(0, 5)]
        triangles, constrained_edges = constrained_delaunay_triangulation(outer)

        def point_key(point):
            return (round(point.x, 6), round(point.y, 6), point.id)

        def edge_key(a, b):
            return tuple(sorted((point_key(a), point_key(b))))

        edge_map = {}
        for index, triangle in enumerate(triangles):
            for edge in ((triangle[0], triangle[1]), (triangle[1], triangle[2]), (triangle[2], triangle[0])):
                edge_map.setdefault(edge_key(*edge), []).append(index)

        for edge, owners in edge_map.items():
            if edge in constrained_edges or len(owners) != 2:
                continue
            first = triangles[owners[0]]
            second = triangles[owners[1]]
            shared = set(edge)
            a = next(vertex for vertex in first if point_key(vertex) not in shared)
            b = next(vertex for vertex in second if point_key(vertex) not in shared)
            shared_vertices = [vertex for vertex in first if point_key(vertex) in shared]
            c, d = shared_vertices
            self.assertLessEqual(incircle_sign(a, c, d, b), 0)

if __name__ == "__main__":
    unittest.main()
