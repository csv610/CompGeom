import unittest
from compgeom.kernel import Point2D
from compgeom.polygon.polygon import Polygon
from compgeom.verifiers.polygon.decomposition_verifiers import verify_convex_decomposition
from compgeom.verifiers.polygon.polygon_verifiers import verify_simple_polygon


class TestDecompositionVerifiers(unittest.TestCase):
    def test_verify_simple_polygon(self):
        # Simple square
        square = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
        self.assertTrue(verify_simple_polygon(square))

        # Simple L-shape (concave)
        l_shape = [
            Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), 
            Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)
        ]
        self.assertTrue(verify_simple_polygon(l_shape))

        # Self-intersecting polygon (Figure-8)
        fig8 = [Point2D(0, 0), Point2D(2, 2), Point2D(2, 0), Point2D(0, 2)]
        with self.assertRaises(ValueError) as cm:
            verify_simple_polygon(fig8)
        self.assertIn("self-intersecting", str(cm.exception))

        # Duplicate vertex
        duplicate = [Point2D(0, 0), Point2D(1, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)]
        with self.assertRaises(ValueError) as cm:
            verify_simple_polygon(duplicate)
        self.assertIn("duplicate vertex", str(cm.exception))

    def test_convex_polygon_itself(self):
        # A simple square
        square = Polygon([Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])
        decomposition = [square]
        self.assertTrue(verify_convex_decomposition(square, decomposition))

    def test_l_shape_decomposition(self):
        # L-shape: (0,0), (2,0), (2,1), (1,1), (1,2), (0,2)
        # Area = 2*1 + 1*1 = 3
        l_shape = Polygon([
            Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), 
            Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)
        ])
        
        # Decompose into two rectangles:
        # 1. (0,0), (2,0), (2,1), (0,1)  (Area 2)
        # 2. (0,1), (1,1), (1,2), (0,2)  (Area 1)
        part1 = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), Point2D(0, 1)])
        part2 = Polygon([Point2D(0, 1), Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)])
        
        decomposition = [part1, part2]
        self.assertTrue(verify_convex_decomposition(l_shape, decomposition))

    def test_invalid_area_decomposition(self):
        square = Polygon([Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)])
        # Part that is too small
        part1 = Polygon([Point2D(0, 0), Point2D(0.5, 0), Point2D(0.5, 0.5), Point2D(0, 0.5)])
        
        with self.assertRaises(ValueError) as cm:
            verify_convex_decomposition(square, [part1])
        self.assertIn("does not match original area", str(cm.exception))

    def test_non_convex_part(self):
        # Original is a large square
        square = Polygon([Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)])
        # Decomposition contains an L-shape (non-convex)
        l_shape_part = Polygon([
            Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), 
            Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)
        ])
        # Remaining part: a small square (1,1), (2,1), (2,2), (1,2)
        rest = Polygon([Point2D(1, 1), Point2D(2, 1), Point2D(2, 2), Point2D(1, 2)])
        
        with self.assertRaises(ValueError) as cm:
            verify_convex_decomposition(square, [l_shape_part, rest])
        self.assertIn("is not convex", str(cm.exception))

    def test_part_outside_original(self):
        # L-shape again
        l_shape = Polygon([
            Point2D(0, 0), Point2D(2, 0), Point2D(2, 1), 
            Point2D(1, 1), Point2D(1, 2), Point2D(0, 2)
        ])
        # A triangle that spans the "concavity" (1,1)-(2,1)-(1,2) gap
        # Vertices are on boundary: (1,1), (2,1), (1,2)
        # But centroid is outside!
        bad_part = Polygon([Point2D(1, 1), Point2D(2, 1), Point2D(1, 2)])
        
        # The centroid of (1,1), (2,1), (1,2) is (1.33, 1.33)
        # For L-shape, (1.33, 1.33) is outside.
        
        # Area of L-shape is 3. 
        # If we add other parts to make area 3, this bad part should be caught by centroid check.
        
        # Actually, let's just check if it raises ValueError for the bad part.
        with self.assertRaises(ValueError) as cm:
             verify_convex_decomposition(l_shape, [bad_part])
        self.assertIn("outside original polygon", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
