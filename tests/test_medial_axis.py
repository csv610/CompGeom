import unittest
from compgeom.kernel import Point2D
from compgeom.polygon.medial_axis import approximate_medial_axis

class MedialAxisTests(unittest.TestCase):
    def test_square_medial_axis_produces_interior_graph(self):
        polygon = [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]
        result = approximate_medial_axis(polygon, resolution=0.5)
        self.assertGreater(len(result["samples"]), 4)
        self.assertGreater(len(result["centers"]), 0)
        self.assertGreater(len(result["segments"]), 0)
        for start, end in result["segments"]:
            self.assertTrue(0.0 <= start.x <= 2.0 and 0.0 <= start.y <= 2.0)
            self.assertTrue(0.0 <= end.x <= 2.0 and 0.0 <= end.y <= 2.0)

if __name__ == "__main__":
    unittest.main()
