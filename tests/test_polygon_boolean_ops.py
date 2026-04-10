import unittest
from compgeom.kernel import Point2D
from compgeom.cli.polygon_boolean_operations_cli import apply_boolean_operation

class PolygonBooleanTests(unittest.TestCase):
    def test_difference_with_nested_polygon_returns_region_with_hole(self):
        outer = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4)]
        inner = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
        result = apply_boolean_operation(outer, inner, "difference")
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["holes"]), 1)
        self.assertEqual(len(result[0]["outer"]), 4)
        self.assertEqual(len(result[0]["holes"][0]), 4)

    def test_union_of_overlapping_rectangles_returns_single_region(self):
        left = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
        right = [Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)]
        result = apply_boolean_operation(left, right, "union")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["holes"], [])

if __name__ == "__main__":
    unittest.main()
