"""Swarovski Crystal generation from raw diamond meshes."""

import argparse
import sys
import random
from typing import List

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
    from compgeom.mesh.surface.convex_hull import ConvexHull3D
    from compgeom.mesh.surface.mesh_decimation import MeshDecimator
    from compgeom.mesh.surface.mesh_processing import MeshProcessing
except ImportError:
    TriMesh = object
    Point3D = object
    ConvexHull3D = object
    MeshDecimator = object
    MeshProcessing = object


class SwarovskiCrystals:
    """Provides algorithms for converting raw gemstone meshes into precision-cut crystals."""

    @staticmethod
    def center_points(points: List[Point3D]) -> List[Point3D]:
        """Centers points around the origin (0, 0, 0)."""
        if not points:
            return []
        count = len(points)
        cx = sum(p.x for p in points) / count
        cy = sum(p.y for p in points) / count
        cz = sum(p.z for p in points) / count
        return [Point3D(p.x - cx, p.y - cy, p.z - cz) for p in points]

    @staticmethod
    def symmetrize_points(points: List[Point3D], planes: str = "xy") -> List[Point3D]:
        """
        Enforces symmetry by reflecting points across specified planes.
        'x' reflect across y-z plane (x=0), 'y' reflect across x-z plane (y=0), etc.
        """
        sym_points = list(points)
        # Note: Centering is crucial for meaningful symmetry planes
        sym_points = SwarovskiCrystals.center_points(sym_points)

        for char in planes.lower():
            if char == "x":
                sym_points += [Point3D(-p.x, p.y, p.z) for p in sym_points]
            elif char == "y":
                sym_points += [Point3D(p.x, -p.y, p.z) for p in sym_points]
            elif char == "z":
                sym_points += [Point3D(p.x, p.y, -p.z) for p in sym_points]

        # Simple quantization for deduplication
        unique_pts = []
        seen = set()
        for p in sym_points:
            key = (round(p.x, 8), round(p.y, 8), round(p.z, 8))
            if key not in seen:
                seen.add(key)
                unique_pts.append(p)
        return unique_pts

    @staticmethod
    def convert_raw_diamond_to_crystal(
        mesh: TriMesh,
        target_faces: int = 48,
        smoothing_iterations: int = 10,
        symmetry_planes: str = "xy",
    ) -> TriMesh:
        """
        Processes a 'raw' diamond mesh into a Swarovski crystal.
        Objectives fulfillment:
        (1) Almost convex: Uses Convex Hull algorithm which guarantees convexity.
        (2) No sharp corners: Uses Taubin Smoothing to round off vertices without shrinkage.
        (3) Low faces: Uses Mesh Decimation to simplify to a faceted look.
        (4) Planar faces: Inherited from the Convex Hull geometry.
        (5) Symmetry: Mirroring points across principal planes before hulling.
        """
        # Step 1: Enforce Symmetry (Objective 5)
        # Mirroring the point cloud ensures the resulting Hull is perfectly symmetric.
        sym_vertices = SwarovskiCrystals.symmetrize_points(
            mesh.vertices, symmetry_planes
        )

        # Step 2: Convexity & Planarity (Objectives 1 & 4)
        # The Convex Hull is the fundamental 'diamond' shape.
        # All triangles on a large facet will be coplanar.
        hull = ConvexHull3D.compute(sym_vertices)

        # Step 3: Decimate (Objective 3)
        # Reduce complexity to a fixed number of facets for a stylized crystal appearance.
        if len(hull.faces) > target_faces:
            crystal = MeshDecimator.decimate(hull, target_faces)
        else:
            crystal = hull

        # Step 4: No Sharp Corners (Objective 2)
        # Taubin smoothing is a feature-preserving smoothing that avoids the 'blob'
        # effect of Laplacian smoothing while still rounding off sharp corners.
        if smoothing_iterations > 0:
            crystal = MeshProcessing.taubin_smoothing(
                crystal, iterations=smoothing_iterations
            )

        return crystal


def main():
    parser = argparse.ArgumentParser(
        description="Swarovski Crystal generation from raw diamond meshes."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # convert subparser
    convert_parser = subparsers.add_parser("convert", help="Processes a 'raw' diamond mesh into a Swarovski crystal")
    convert_parser.add_argument("--input", help="Path to raw diamond mesh (.stl, .obj)")
    convert_parser.add_argument(
        "--faces", type=int, default=32, help="Target number of facets (default: 32)"
    )
    convert_parser.add_argument(
        "--smooth",
        type=int,
        default=10,
        help="Smoothing iterations for corners (default: 10)",
    )
    convert_parser.add_argument(
        "--symmetry",
        type=str,
        default="xy",
        help="Symmetry planes (combinations of x,y,z e.g., 'xy')",
    )

    # center subparser
    center_parser = subparsers.add_parser("center", help="Centers mesh vertices around the origin")
    center_parser.add_argument("--input", required=True, help="Path to mesh file")

    # symmetrize subparser
    sym_parser = subparsers.add_parser("symmetrize", help="Enforces symmetry by reflecting points across specified planes")
    sym_parser.add_argument("--input", required=True, help="Path to mesh file")
    sym_parser.add_argument("--planes", type=str, default="xy", help="Symmetry planes (e.g., 'xy')")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    print(f"--- Swarovski Crystal Generator: {args.command} ---")

    try:
        raw_mesh = None
        if hasattr(args, "input") and args.input:
            print(f"Loading mesh from: {args.input}")
            try:
                from compgeom.mesh.meshio import from_file
                verts, faces = from_file(args.input)
                raw_mesh = TriMesh(verts, faces)
            except ImportError:
                print("Error: compgeom.mesh.meshio not available for loading files.")
                return
        elif args.command == "convert":
            print("No input provided. Generating a raw diamond placeholder...")
            # Create a noisy octahedron-like point cloud
            pts = [
                Point3D(1.0, 0, 0),
                Point3D(-1.0, 0, 0),
                Point3D(0, 1.0, 0),
                Point3D(0, -1.0, 0),
                Point3D(0, 0, 1.5),
                Point3D(0, 0, -1.0),
            ]
            # Add noise for 'raw' look
            for _ in range(50):
                pts.append(
                    Point3D(
                        random.uniform(-0.8, 0.8),
                        random.uniform(-0.8, 0.8),
                        random.uniform(-1.2, 1.2),
                    )
                )

            # Use hull to create the raw mesh
            try:
                raw_mesh = ConvexHull3D.compute(pts)
            except Exception:
                # Fallback if ConvexHull3D is mock
                raw_mesh = TriMesh(pts, [])
            print(f"Generated raw mesh with {len(raw_mesh.vertices)} vertices.")

        if not raw_mesh:
            print("Error: No mesh available.")
            return

        tools = SwarovskiCrystals()
        
        if args.command == "convert":
            crystal = tools.convert_raw_diamond_to_crystal(
                raw_mesh,
                target_faces=args.faces,
                smoothing_iterations=args.smooth,
                symmetry_planes=args.symmetry,
            )

            print(f"Conversion complete!")
            if hasattr(crystal, "faces"):
                print(f"  - Final face count: {len(crystal.faces)}")
            print(f"  - Symmetry: Applied ({args.symmetry})")
            print(f"  - Corner Rounding: {args.smooth} iterations applied.")

        elif args.command == "center":
            centered_verts = tools.center_points(raw_mesh.vertices)
            print(f"Centered {len(centered_verts)} vertices.")

        elif args.command == "symmetrize":
            sym_verts = tools.symmetrize_points(raw_mesh.vertices, args.planes)
            print(f"Symmetrized vertices. Total count: {len(sym_verts)} using planes: {args.planes}")

    except Exception as e:
        print(f"Error during processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
