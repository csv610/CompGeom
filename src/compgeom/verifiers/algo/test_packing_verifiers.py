import unittest
from compgeom.algo.rectangle_packing import RectanglePacker, PackedRect
from compgeom.verifiers.algo.packing_verifiers import verify_rectangle_packing


class TestPackingVerifiers(unittest.TestCase):
    def test_valid_packing(self):
        dimensions = [(10, 20), (30, 10), (20, 20)]
        w, h, placements = RectanglePacker.pack(dimensions)
        self.assertTrue(verify_rectangle_packing(dimensions, w, h, placements))

    def test_square_packing(self):
        dimensions = [(10, 10), (10, 10), (10, 10), (10, 10)]
        w, h, placements = RectanglePacker.pack(dimensions, target_shape="square")
        self.assertTrue(verify_rectangle_packing(dimensions, w, h, placements))

    def test_invalid_overlap(self):
        dimensions = [(10, 10), (10, 10)]
        # Manually create overlapping placements
        placements = [
            PackedRect(0, 0, 10, 10, 0),
            PackedRect(5, 5, 10, 10, 1) # Overlaps
        ]
        with self.assertRaises(ValueError) as cm:
            verify_rectangle_packing(dimensions, 20, 20, placements)
        self.assertIn("Overlap detected", str(cm.exception))

    def test_outside_container(self):
        dimensions = [(10, 10)]
        placements = [PackedRect(0, 0, 10, 10, 0)]
        # Container too small
        with self.assertRaises(ValueError) as cm:
            verify_rectangle_packing(dimensions, 5, 5, placements)
        self.assertIn("exceeds container", str(cm.exception))

    def test_missing_rectangle(self):
        dimensions = [(10, 10), (20, 20)]
        placements = [PackedRect(0, 0, 10, 10, 0)]
        with self.assertRaises(ValueError) as cm:
            verify_rectangle_packing(dimensions, 30, 30, placements)
        self.assertIn("Placement count", str(cm.exception))

    def test_duplicate_id(self):
        dimensions = [(10, 10), (20, 20)]
        placements = [
            PackedRect(0, 0, 10, 10, 0),
            PackedRect(10, 0, 10, 10, 0) # Duplicate ID 0
        ]
        with self.assertRaises(ValueError) as cm:
            verify_rectangle_packing(dimensions, 30, 30, placements)
        self.assertIn("Duplicate rectangle id", str(cm.exception))

    def test_wrong_dimensions(self):
        dimensions = [(10, 10)]
        placements = [PackedRect(0, 0, 20, 20, 0)] # Wrong size
        with self.assertRaises(ValueError) as cm:
            verify_rectangle_packing(dimensions, 30, 30, placements)
        self.assertIn("dimensions", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
