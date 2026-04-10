import unittest
from compgeom.kernel import Point2D
from compgeom.polygon.planar import DCEL

class PlanarSubdivisionTests(unittest.TestCase):
    def test_locate_face_for_polygon_with_hole(self):
        dcel = DCEL.from_polygon(
            [Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)],
            holes=[[Point2D(2, 2), Point2D(4, 2), Point2D(4, 4), Point2D(2, 4)]],
        )
        interior = dcel.locate_face(Point2D(1, 1))
        hole_region = dcel.locate_face(Point2D(3, 3))
        exterior = dcel.locate_face(Point2D(7, 3))
        self.assertFalse(interior.is_exterior)
        self.assertTrue(hole_region.is_exterior)
        self.assertTrue(exterior.is_exterior)

    def test_polygon_dcel_has_expected_primitives(self):
        dcel = DCEL.from_polygon([Point2D(0, 0), Point2D(3, 0), Point2D(0, 2)])
        self.assertEqual(len(dcel.vertices), 3)
        self.assertEqual(len(dcel.half_edges), 6)
        self.assertEqual(len(dcel.faces), 2)

if __name__ == "__main__":
    unittest.main()
