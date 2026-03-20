"""Topographical analysis for Civil Engineering (TIN and Contouring)."""

import argparse
from typing import List
import math

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
    from compgeom.mesh.surface.mesh_analysis import MeshAnalysis
    from compgeom.mesh.surface.mesh_queries import MeshQueries
except ImportError:
    TriMesh = object
    Point3D = object
    MeshAnalysis = object
    MeshQueries = object


class TopoAnalysis:
    """Provides algorithms for terrain modeling and contour extraction."""

    @staticmethod
    def extract_contours(mesh: TriMesh, elevation: float) -> List[List[Point3D]]:
        """
        Extracts elevation isocontours from a terrain mesh.
        Returns a list of polylines (contours) at the specified height.
        """
        if not hasattr(MeshQueries, "slice_mesh") or MeshQueries.slice_mesh is object:
             return []

        # This is a specialized slice_mesh for horizontal planes
        segments = MeshQueries.slice_mesh(mesh, (0, 0, elevation), (0, 0, 1))

        # Connect segments into polylines
        if not segments:
            return []

        polylines = []
        visited = [False] * len(segments)

        for i in range(len(segments)):
            if visited[i]:
                continue

            current_poly = [segments[i][0], segments[i][1]]
            visited[i] = True

            # Greedy search for next segment
            found = True
            while found:
                found = False
                for j in range(len(segments)):
                    if visited[j]:
                        continue

                    p1, p2 = segments[j]
                    tail = current_poly[-1]

                    def dist(a, b):
                        return math.sqrt(
                            (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2
                        )

                    if dist(tail, p1) < 1e-8:
                        current_poly.append(p2)
                        visited[j] = True
                        found = True
                        break
                    elif dist(tail, p2) < 1e-8:
                        current_poly.append(p1)
                        visited[j] = True
                        found = True
                        break
            polylines.append(current_poly)

        return polylines

    @staticmethod
    def earthwork_volume(mesh_base: TriMesh, mesh_top: TriMesh) -> float:
        """
        Calculates the volume of soil/material between two surfaces.
        Essential for civil engineering construction sites.
        """
        if not hasattr(MeshAnalysis, "total_volume") or MeshAnalysis.total_volume is object:
            return 0.0
        vol_base = MeshAnalysis.total_volume(mesh_base)  # Assumes closed to Z=0
        vol_top = MeshAnalysis.total_volume(mesh_top)
        return vol_top - vol_base


def main():
    parser = argparse.ArgumentParser(description="Topographical analysis for Civil Engineering (TIN and Contouring).")
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # extract_contours subparser
    contours_parser = subparsers.add_parser("contours", help="Extracts elevation isocontours from a terrain mesh")
    contours_parser.add_argument("--elevation", type=float, required=True, help="Elevation at which to extract contours")

    # earthwork_volume subparser
    volume_parser = subparsers.add_parser("volume", help="Calculates earthwork volume between two surfaces")

    args = parser.parse_args()
    tools = TopoAnalysis()

    # Mock meshes for demo/default
    class MockMesh:
        def __init__(self, name):
            self.name = name

    mesh_base = MockMesh("base")
    mesh_top = MockMesh("top")

    if args.command == "contours":
        contours = tools.extract_contours(mesh_base, args.elevation)
        print(f"Extracted {len(contours)} contours at elevation {args.elevation}")
    elif args.command == "volume":
        volume = tools.earthwork_volume(mesh_base, mesh_top)
        print(f"Earthwork Volume: {volume:.2f} cubic units")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
