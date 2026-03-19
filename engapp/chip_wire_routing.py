"""VLSI Chip Wire Routing and Rectilinear Pathfinding algorithms."""

import math
import heapq
import argparse
from typing import List, Tuple, Set, Dict, Optional

try:
    from compgeom.mesh import TriMesh
    from compgeom.kernel import Point3D
except ImportError:
    raise ImportError("Required compgeom modules not found. Please install compgeom package.")


class ChipWireRouter:
    """Provides algorithms for rectilinear wire routing in VLSI design."""

    @staticmethod
    def manhattan_distance(p1: Tuple[int, int, int], p2: Tuple[int, int, int]) -> int:
        """Calculates the L1 (Manhattan) distance between two grid points."""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]) + abs(p1[2] - p2[2])

    @staticmethod
    def find_rectilinear_path(
        start: Tuple[int, int, int],
        end: Tuple[int, int, int],
        grid_size: Tuple[int, int, int],
        obstacles: Set[Tuple[int, int, int]],
        via_cost: int = 5,
    ) -> Optional[List[Tuple[int, int, int]]]:
        """
        Finds the shortest rectilinear path between two points using A* search.
        Minimizes total length and the number of layer changes (Vias).
        """
        # (priority, cost_so_far, current_pos, path)
        open_set = []
        heapq.heappush(open_set, (0, 0, start, [start]))

        visited = {}  # pos -> cost_so_far

        while open_set:
            _, cost, current, path = heapq.heappop(open_set)

            if current == end:
                return path

            if current in visited and visited[current] <= cost:
                continue
            visited[current] = cost

            # Neighbors: 6 directions (rectilinear)
            for dx, dy, dz in [
                (1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            ]:
                nx, ny, nz = current[0] + dx, current[1] + dy, current[2] + dz

                # Bounds check
                if not (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                    and 0 <= nz < grid_size[2]
                ):
                    continue

                neighbor = (nx, ny, nz)
                if neighbor in obstacles:
                    continue

                # Cost calculation
                # Base step cost is 1. If we change layers (dz != 0), add via_cost.
                step_cost = 1 + (via_cost if dz != 0 else 0)
                new_cost = cost + step_cost

                priority = new_cost + ChipWireRouter.manhattan_distance(neighbor, end)
                heapq.heappush(
                    open_set, (priority, new_cost, neighbor, path + [neighbor])
                )

        return None

    @staticmethod
    def calculate_wire_congestion(
        routed_nets: List[List[Tuple[int, int, int]]], grid_size: Tuple[int, int, int]
    ) -> Dict[Tuple[int, int], float]:
        """
        Analyzes the routing density across the chip area.
        Returns a map of (x, y) coordinates to congestion percentages.
        """
        usage = {}
        for net in routed_nets:
            for x, y, z in net:
                usage[(x, y)] = usage.get((x, y), 0) + 1

        congestion = {}
        max_capacity_per_pixel = grid_size[2]  # Max wires = number of layers
        for loc, count in usage.items():
            congestion[loc] = (count / max_capacity_per_pixel) * 100.0

        return congestion


def main():
    parser = argparse.ArgumentParser(
        description="VLSI Chip Wire Routing and Rectilinear Pathfinding algorithms."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available tools")

    # Manhattan Distance
    dist_parser = subparsers.add_parser("distance", help="Calculates Manhattan distance")
    dist_parser.add_argument("--p1", type=int, nargs=3, required=True)
    dist_parser.add_argument("--p2", type=int, nargs=3, required=True)

    # Find Rectilinear Path
    path_parser = subparsers.add_parser("find-path", help="Finds the shortest rectilinear path")
    path_parser.add_argument("--start", type=int, nargs=3, required=True)
    path_parser.add_argument("--end", type=int, nargs=3, required=True)
    path_parser.add_argument("--grid", type=int, nargs=3, required=True, help="Grid size X Y Z")
    path_parser.add_argument("--obstacles", type=int, nargs="+", help="Obstacles as x1 y1 z1 x2 y2 z2...")
    path_parser.add_argument("--via-cost", type=int, default=5)

    # Calculate Congestion
    cong_parser = subparsers.add_parser("congestion", help="Analyzes the routing density")
    cong_parser.add_argument("--grid", type=int, nargs=3, required=True)
    cong_parser.add_argument("--nets", type=int, nargs="+", help="Nets as net1_x1 net1_y1 net1_z1 net1_x2... ; separator needed?")
    # Simple net input for CLI: x1 y1 z1 x2 y2 z2 | x3 y3 z3 x4 y4 z4 ...
    # But argparse doesn't handle nested lists easily. Let's simplify: one net at a time or multiple points for one net.
    cong_parser.add_argument("--net", type=int, nargs="+", help="Points for one net: x1 y1 z1 x2 y2 z2...")

    args = parser.parse_args()

    if args.command == "distance":
        d = ChipWireRouter.manhattan_distance(tuple(args.p1), tuple(args.p2))
        print(f"Manhattan distance: {d}")
    elif args.command == "find-path":
        obs = set()
        if args.obstacles:
            for i in range(0, len(args.obstacles), 3):
                obs.add((args.obstacles[i], args.obstacles[i+1], args.obstacles[i+2]))
        path = ChipWireRouter.find_rectilinear_path(
            tuple(args.start), tuple(args.end), tuple(args.grid), obs, args.via_cost
        )
        print(f"Path: {path}")
    elif args.command == "congestion":
        net = []
        if args.net:
            for i in range(0, len(args.net), 3):
                net.append((args.net[i], args.net[i+1], args.net[i+2]))
        cong = ChipWireRouter.calculate_wire_congestion([net], tuple(args.grid))
        print(f"Congestion map: {cong}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
