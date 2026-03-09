import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"


class CliRegressionTests(unittest.TestCase):
    def run_script(self, script_name, stdin_text):
        module_name = script_name.replace('.py', '')
        pythonpath = str(SRC)
        existing_pythonpath = os.environ.get("PYTHONPATH")
        if existing_pythonpath:
            pythonpath = f"{pythonpath}{os.pathsep}{existing_pythonpath}"
        env = dict(os.environ, PYTHONPATH=pythonpath)
        completed = subprocess.run(
            [sys.executable, "-m", "compgeom.cli.main", module_name],
            input=stdin_text,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        return completed

    def test_smallest_enclosing_circle_cli_runs(self):
        completed = self.run_script(
            "smallest_enclosing_circle.py",
            "0 0\n1 0\n0 1\n",
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Smallest Enclosing Circle:", completed.stdout)
        self.assertIn("Radius:", completed.stdout)

    def test_mesh_neighbors_cli_query(self):
        completed = self.run_script(
            "mesh_neighbors.py",
            "0 0 0\n1 1 0\n2 0 1\n3 1 1\nT\n0 1 2\n1 3 2\nP 1\nF 0\n",
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Point 1 neighbors: [0, 2, 3]", completed.stdout)
        self.assertIn("Triangle 0 neighbors: [1]", completed.stdout)

    def test_line_arrangement_cli_rectangle(self):
        completed = self.run_script(
            "line_arrangement.py",
            "0 0 1 0\n1 0 1 1\n1 1 0 1\n0 1 0 0\n",
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Intersection Points:", completed.stdout)
        self.assertIn("Non-Intersecting Segments:", completed.stdout)
        self.assertIn("Polygons:", completed.stdout)
        self.assertIn("(1.000000, 1.000000)", completed.stdout)

    def test_polygon_visibility_cli_reports_subdivided_segments(self):
        completed = self.run_script(
            "polygon_visibility.py",
            "1 2.5\n0 0\n5 0\n5 1\n2 1\n2 4\n5 4\n5 5\n0 5\n",
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        self.assertIn("Visible Segments:", completed.stdout)
        self.assertIn("(2.666667, 0.000000)", completed.stdout)
        self.assertIn("(2.000000, 1.000000) -> (2.000000, 4.000000)", completed.stdout)


if __name__ == "__main__":
    unittest.main()
