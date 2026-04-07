import unittest
from compgeom.algo.random_walker import generate_spiral_path, generate_spiral_path_3d
from compgeom.verifiers.algo.walker_verifiers import (
    verify_spiral_walker_2d,
    verify_spiral_walker_3d,
)


class TestWalkerVerifiers(unittest.TestCase):
    def test_spiral_walker_2d(self):
        width, height = 5, 5
        path = generate_spiral_path(width, height)
        self.assertTrue(verify_spiral_walker_2d(path, width, height))

    def test_spiral_walker_2d_small(self):
        width, height = 2, 2
        path = generate_spiral_path(width, height)
        self.assertTrue(verify_spiral_walker_2d(path, width, height))

    def test_spiral_walker_3d(self):
        width, height, depth = 3, 3, 3
        path = generate_spiral_path_3d(width, height, depth)
        self.assertTrue(verify_spiral_walker_3d(path, width, height, depth))

    def test_invalid_length_2d(self):
        with self.assertRaises(ValueError):
            verify_spiral_walker_2d([(0, 0), (1, 0)], 2, 2)

    def test_invalid_adjacency_2d(self):
        # Jump from (0,0) to (1,1)
        path = [(0, 0), (1, 1), (1, 0), (0, 1)]
        with self.assertRaises(ValueError) as cm:
            verify_spiral_walker_2d(path, 2, 2)
        self.assertIn("not adjacent", str(cm.exception))

    def test_duplicate_visit_2d(self):
        path = [(0, 0), (1, 0), (1, 0), (0, 0)] # Not actually possible to be both duplicate and adjacent here but let's see
        # Let's make a better duplicate:
        path = [(0, 0), (1, 0), (1, 1), (1, 0)]
        # This will fail adjacency first probably if we are not careful.
        # (1,1) to (1,0) IS adjacent.
        # (0,0), (1,0), (1,1), (1,0)
        with self.assertRaises(ValueError) as cm:
            verify_spiral_walker_2d(path, 2, 2)
        self.assertIn("already visited", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
