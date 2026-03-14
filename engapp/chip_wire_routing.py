"""VLSI Chip Wire Routing and Rectilinear Pathfinding algorithms."""

import math
import heapq
from typing import List, Tuple, Set, Dict, Optional

try:
    from compgeom.mesh import TriangleMesh
    from compgeom.kernel import Point3D
except ImportError:

    class TriangleMesh:
        def __init__(self, vertices=None, faces=None):
            self.vertices = vertices or []
            self.faces = faces or []

    class Point3D:
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x = x
            self.y = y
            self.z = z


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
    print("--- chip_wire_routing.py Demo ---")

    # 1. Setup Chip Grid (10x10 units, 3 Layers)
    size = (10, 10, 3)

    # 2. Add obstacles (e.g., pre-placed logic blocks)
    # Block a rectangle in the middle of Layer 0
    obs = set()
    for x in range(3, 7):
        for y in range(3, 7):
            obs.add((x, y, 0))

    print(f"Chip Grid: {size[0]}x{size[1]} with {size[2]} layers.")
    print(f"Obstacle block placed at center of Layer 0.")

    # 3. Route a wire from (0,0,0) to (9,9,0)
    source = (0, 0, 0)
    sink = (9, 9, 0)

    print(f"\nRouting net from {source} to {sink}...")
    path = ChipWireRouter.find_rectilinear_path(source, sink, size, obs)

    if path:
        print(f"Path found! Length: {len(path)} segments.")
        # Check if it used Vias (Layer changes)
        layers_used = set(p[2] for p in path)
        print(f"Layers utilized: {list(layers_used)}")
        if len(layers_used) > 1:
            print("Router successfully used Vias to bypass obstacles.")
    else:
        print("No valid path found.")

    # 4. Congestion Analysis
    if path:
        cong = ChipWireRouter.calculate_wire_congestion([path], size)
        max_c = max(cong.values())
        print(f"\nPeak Routing Congestion: {max_c:.1f}%")

    print("\nDemo completed successfully.")


if __name__ == "__main__":
    main()
