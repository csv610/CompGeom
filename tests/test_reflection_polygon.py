import unittest
from compgeom.kernel import Point2D
from compgeom.cli.reflection_polygon_cli import parse_input, simulate_reflections

class ReflectionPolygonTests(unittest.TestCase):
    def test_parse_input_normalizes_direction_and_preserves_polygon(self):
        origin, direction, polygon = parse_input(
            [
                "1 1\n",
                "3 4\n",
                "0 0\n",
                "5 0\n",
                "5 5\n",
                "0 5\n",
            ]
        )
        self.assertEqual(origin, Point2D(1, 1))
        self.assertAlmostEqual(direction.x, 0.6, places=6)
        self.assertAlmostEqual(direction.y, 0.8, places=6)
        self.assertEqual(len(polygon), 4)

    def test_reflection_path_bounces_between_parallel_walls(self):
        polygon = [Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2)]
        path = simulate_reflections(
            origin=Point2D(1, 1),
            direction=Point2D(1, 0.25),
            polygon=polygon,
            steps=4,
        )
        self.assertEqual(len(path), 5)
        self.assertAlmostEqual(path[1].x, 4.0, places=6)
        self.assertAlmostEqual(path[1].y, 1.75, places=6)
        self.assertAlmostEqual(path[2].x, 3.0, places=6)
        self.assertAlmostEqual(path[2].y, 2.0, places=6)
        self.assertAlmostEqual(path[3].x, 0.0, places=6)
        self.assertAlmostEqual(path[3].y, 1.25, places=6)
        self.assertAlmostEqual(path[4].x, 4.0, places=6)
        self.assertAlmostEqual(path[4].y, 0.25, places=6)

    def test_parse_input_rejects_origin_outside_polygon(self):
        with self.assertRaisesRegex(ValueError, "inside or on the boundary"):
            parse_input(
                [
                    "10 10\n",
                    "1 0\n",
                    "0 0\n",
                    "4 0\n",
                    "4 4\n",
                    "0 4\n",
                ]
            )

if __name__ == "__main__":
    unittest.main()
