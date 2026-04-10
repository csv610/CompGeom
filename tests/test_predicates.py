import unittest
from compgeom.kernel import Point2D, orientation_sign, incircle_sign

class PredicateRobustnessTests(unittest.TestCase):
    def test_orientation_sign_handles_nearly_collinear_points(self):
        a = Point2D(0.0, 0.0)
        b = Point2D(1e-12, 1e-12)
        c = Point2D(2e-12, 3e-12)
        self.assertEqual(orientation_sign(a, b, c), 1)

    def test_incircle_sign_is_orientation_aware(self):
        a = Point2D(0, 0)
        b = Point2D(1, 0)
        c = Point2D(0, 1)
        inside = Point2D(0.2, 0.2)
        outside = Point2D(2, 2)
        self.assertEqual(incircle_sign(a, b, c, inside), 1)
        self.assertEqual(incircle_sign(c, b, a, inside), 1)
        self.assertEqual(incircle_sign(a, b, c, outside), -1)

if __name__ == "__main__":
    unittest.main()
