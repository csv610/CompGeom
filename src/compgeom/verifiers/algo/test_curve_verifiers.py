import unittest
from compgeom.algo.space_filling_curves import SpaceFillingCurves
from compgeom.verifiers.algo.curve_verifiers import verify_morton_curve, verify_peano_curve, verify_hilbert_curve

class TestCurveVerifiers(unittest.TestCase):
    def test_hilbert_order_1(self):
        order = 1
        path = SpaceFillingCurves.hilbert(order)
        self.assertEqual(len(path), 4)
        self.assertTrue(verify_hilbert_curve(path, order))

    def test_hilbert_order_2(self):
        order = 2
        path = SpaceFillingCurves.hilbert(order)
        self.assertEqual(len(path), 16)
        self.assertTrue(verify_hilbert_curve(path, order))

    def test_hilbert_invalid_length(self):
        with self.assertRaises(ValueError):
            verify_hilbert_curve([0]*3, 1)

    def test_peano_level_1(self):
        level = 1
        path = SpaceFillingCurves.peano(level)
        self.assertEqual(len(path), 9)
        self.assertTrue(verify_peano_curve(path, level))

    def test_peano_level_2(self):
        level = 2
        path = SpaceFillingCurves.peano(level)
        self.assertEqual(len(path), 81)
        self.assertTrue(verify_peano_curve(path, level))

    def test_peano_invalid_length(self):
        with self.assertRaises(ValueError):
            verify_peano_curve([0]*8, 1)

    def test_morton_level_1(self):
        level = 1
        path = SpaceFillingCurves.morton(level)
        # Expected Z-order for 2x2: (0,0), (1,0), (0,1), (1,1)
        # y*width + x:
        # 0*2 + 0 = 0
        # 0*2 + 1 = 1
        # 1*2 + 0 = 2
        # 1*2 + 1 = 3
        self.assertEqual(path, [0, 1, 2, 3])
        self.assertTrue(verify_morton_curve(path, level))

    def test_morton_level_2(self):
        level = 2
        path = SpaceFillingCurves.morton(level)
        self.assertTrue(verify_morton_curve(path, level))

    def test_morton_invalid_length(self):
        with self.assertRaises(ValueError) as cm:
            verify_morton_curve([0, 1, 2], 1)
        self.assertIn("path length", str(cm.exception))

    def test_morton_duplicate(self):
        with self.assertRaises(ValueError) as cm:
            verify_morton_curve([0, 1, 1, 3], 1)
        self.assertIn("Duplicate index", str(cm.exception))

    def test_morton_wrong_order(self):
        # Swap 1 and 2
        with self.assertRaises(ValueError) as cm:
            verify_morton_curve([0, 2, 1, 3], 1)
        self.assertIn("Path mismatch", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
