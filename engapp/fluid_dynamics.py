"""Computational Fluid Dynamics (CFD) geometry preparation tools."""

import argparse
from typing import Tuple

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:

    class TriangleMesh:
        def __init__(self, vertices=None, faces=None):
            self.vertices = vertices or []
            self.faces = faces or []

        def bounding_box(self):
            if not self.vertices:
                return (0, 0, 0), (0, 0, 0)
            xs = [v.x for v in self.vertices]
            ys = [v.y for v in self.vertices]
            zs = [v.z for v in self.vertices]
            return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    class Point3D:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x, self.y, self.z = x, y, z


class FluidDynamics:
    """Provides algorithms for preparing geometry for fluid flow simulations."""

    @staticmethod
    def calculate_frontal_area(
        mesh: TriangleMesh, flow_direction: Tuple[float, float, float]
    ) -> float:
        """
        Calculates the projected frontal area of an object facing the flow direction.
        Used for drag coefficient calculations.
        """
        # Mock implementation for standalone execution
        return 2.5

    @staticmethod
    def generate_wind_tunnel_domain(
        mesh: TriangleMesh,
        padding_front: float = 2.0,
        padding_back: float = 5.0,
        padding_sides: float = 2.0,
    ) -> TriangleMesh:
        """
        Generates a bounding box representing the fluid domain (wind tunnel) around an object.
        """
        mesh.bounding_box()
        # Mock generating a box mesh
        vertices = [Point3D() for _ in range(8)]
        faces = [[0, 1, 2] for _ in range(12)]
        return TriangleMesh(vertices, faces)


def main():
    parser = argparse.ArgumentParser(description="Computational Fluid Dynamics (CFD) geometry preparation tools.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # calculate_frontal_area
    area_parser = subparsers.add_parser(
        "calculate_frontal_area",
        help="Calculates the projected frontal area of an object facing the flow direction.",
    )
    area_parser.add_argument(
        "--flow_direction",
        type=float,
        nargs=3,
        default=[1.0, 0.0, 0.0],
        help="Flow direction vector (default: 1.0 0.0 0.0)",
    )

    # generate_wind_tunnel_domain
    domain_parser = subparsers.add_parser(
        "generate_wind_tunnel_domain",
        help="Generates a bounding box representing the fluid domain (wind tunnel) around an object.",
    )
    domain_parser.add_argument(
        "--padding_front",
        type=float,
        default=2.0,
        help="Padding at the front of the domain (default: 2.0)",
    )
    domain_parser.add_argument(
        "--padding_back",
        type=float,
        default=5.0,
        help="Padding at the back of the domain (default: 5.0)",
    )
    domain_parser.add_argument(
        "--padding_sides",
        type=float,
        default=2.0,
        help="Padding at the sides of the domain (default: 2.0)",
    )

    args = parser.parse_args()

    # Create a mock mesh
    mock_mesh = TriangleMesh([Point3D(0, 0, 0)], [[0, 0, 0]])
    cfd = FluidDynamics()

    if args.command == "calculate_frontal_area":
        area = cfd.calculate_frontal_area(mock_mesh, tuple(args.flow_direction))
        print(f"Calculated frontal area (flow along {args.flow_direction}): {area} sq meters.")
    elif args.command == "generate_wind_tunnel_domain":
        domain = cfd.generate_wind_tunnel_domain(
            mock_mesh, args.padding_front, args.padding_back, args.padding_sides
        )
        print(f"Generated wind tunnel domain with {len(domain.vertices)} vertices.")
    else:
        # Default behavior: run demo
        print("--- fluid_dynamics.py Demo ---")
        domain = cfd.generate_wind_tunnel_domain(mock_mesh)
        print(f"Generated wind tunnel domain with {len(domain.vertices)} vertices.")
        area = cfd.calculate_frontal_area(mock_mesh, (1, 0, 0))
        print(f"Calculated frontal area (flow along X): {area} sq meters.")
        print("\nUse --help to see CLI options.")


if __name__ == "__main__":
    main()
