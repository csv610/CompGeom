"""Molecular geometry algorithms for drug design."""

import argparse
import math
import sys
from typing import List

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
    from compgeom.mesh.volmesh.marching_cubes import MarchingCubes
except ImportError:
    TriMesh = object
    Point3D = object
    MarchingCubes = object


class MolecularGeometry:
    """Provides algorithms for analyzing molecular surfaces and volumes."""

    @staticmethod
    def compute_sas(
        atomic_coordinates: List[Point3D],
        atomic_radii: List[float],
        probe_radius: float = 1.4,
    ) -> TriMesh:
        """
        Computes the Solvent Accessible Surface (SAS) of a molecule.
        Reconstructs the surface by rolling a spherical probe over the atoms.
        Approximated via Marching Cubes on a distance field.
        """

        # 1. Define the distance field: min(dist(p, atom_i) - (radius_i + probe))
        def sas_field(x, y, z):
            min_val = 1e9
            for p, r in zip(atomic_coordinates, atomic_radii):
                dist = math.sqrt((x - p.x) ** 2 + (y - p.y) ** 2 + (z - p.z) ** 2)
                val = dist - (r + probe_radius)
                if val < min_val:
                    min_val = val
            return min_val

        # 2. Determine bounding box
        min_x = min(
            p.x - (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii)
        )
        max_x = max(
            p.x + (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii)
        )
        min_y = min(
            p.y - (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii)
        )
        max_y = max(
            p.y + (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii)
        )
        min_z = min(
            p.z - (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii)
        )
        max_z = max(
            p.z + (r + probe_radius) for p, r in zip(atomic_coordinates, atomic_radii)
        )

        # 3. Extract isosurface at 0.0
        return MarchingCubes.reconstruct(
            sas_field, (min_x, min_y, min_z), (max_x, max_y, max_z), resolution=40
        )

    @staticmethod
    def molecular_volume(mesh: TriMesh) -> float:
        """Calculates the volume of the molecular surface (SAS or SES)."""
        try:
            from compgeom.mesh.surfmesh.mesh_analysis import MeshAnalysis
        except ImportError as e:
            raise ImportError(
                "Could not import MeshAnalysis. Please ensure 'compgeom' package is properly installed."
            ) from e

        return MeshAnalysis.total_volume(mesh)

    @staticmethod
    def detect_pockets(mesh: TriMesh, min_depth: float) -> List[List[int]]:
        """
        Identifies potential binding pockets/cavities on the protein surface.
        Uses Mean Curvature to find concave regions.
        """
        try:
            from compgeom.mesh.surfmesh.curvature import MeshCurvature
        except ImportError as e:
            raise ImportError(
                "Could not import MeshCurvature. Please ensure 'compgeom' package is properly installed."
            ) from e

        mean_k = MeshCurvature.mean_curvature(mesh)

        # Pockets are regions of high negative mean curvature
        pocket_verts = [
            i for i, k in enumerate(mean_k) if k > min_depth
        ]  # Adjusting for magnitude sign

        # Cluster pocket vertices into individual cavities
        from collections import deque

        pockets = []
        visited = set()

        v2v = mesh.topology.vertex_neighbors_map()

        for v_idx in pocket_verts:
            if v_idx in visited:
                continue

            # BFS to find connected concave patch
            current_pocket = []
            queue = deque([v_idx])
            visited.add(v_idx)

            while queue:
                curr = queue.popleft()
                current_pocket.append(curr)
                for nb in v2v.get(curr, []):
                    if nb in pocket_verts and nb not in visited:
                        visited.add(nb)
                        queue.append(nb)
            pockets.append(current_pocket)

        return pockets


def main():
    parser = argparse.ArgumentParser(description="Molecular geometry algorithms for drug design.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common arguments
    def add_common_args(subparser):
        subparser.add_argument(
            "--atoms",
            type=str,
            required=True,
            help="Space-separated x,y,z coordinates (e.g. '0,0,0 2,0,0')",
        )
        subparser.add_argument(
            "--radii",
            type=str,
            required=True,
            help="Space-separated radii values (e.g. '1.5 1.5')",
        )
        subparser.add_argument(
            "--probe", type=float, default=1.4, help="Probe radius (default: 1.4)"
        )

    # Compute SAS
    sas_parser = subparsers.add_parser("compute-sas", help="Compute Solvent Accessible Surface")
    add_common_args(sas_parser)

    # Molecular Volume
    vol_parser = subparsers.add_parser("molecular-volume", help="Calculate molecular volume")
    add_common_args(vol_parser)

    # Detect Pockets
    pocket_parser = subparsers.add_parser("detect-pockets", help="Identify binding pockets")
    add_common_args(pocket_parser)
    pocket_parser.add_argument(
        "--min-depth",
        type=float,
        default=0.5,
        help="Minimum depth for pocket detection (default: 0.5)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Process atoms
    try:
        atom_coords = []
        for a in args.atoms.split():
            x, y, z = map(float, a.split(","))
            atom_coords.append(Point3D(x, y, z))
    except Exception:
        print("Error parsing atoms. Format should be 'x,y,z x,y,z ...'")
        sys.exit(1)

    # Process radii
    try:
        radii = [float(r) for r in args.radii.split()]
    except Exception:
        print("Error parsing radii. Format should be 'r1 r2 ...'")
        sys.exit(1)

    if len(atom_coords) != len(radii):
        print(f"Mismatch: {len(atom_coords)} atoms but {len(radii)} radii provided.")
        sys.exit(1)

    tools = MolecularGeometry()
    try:
        if args.command == "compute-sas":
            sas_mesh = tools.compute_sas(atom_coords, radii, args.probe)
            print(f"Computed SAS mesh with {len(sas_mesh.vertices)} vertices.")

        elif args.command == "molecular-volume":
            sas_mesh = tools.compute_sas(atom_coords, radii, args.probe)
            vol = tools.molecular_volume(sas_mesh)
            print(f"Molecular volume: {vol:.4f}")

        elif args.command == "detect-pockets":
            sas_mesh = tools.compute_sas(atom_coords, radii, args.probe)
            pockets = tools.detect_pockets(sas_mesh, args.min_depth)
            print(f"Detected {len(pockets)} pockets.")
    except Exception as e:
        print(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
