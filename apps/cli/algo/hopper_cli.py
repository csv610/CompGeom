from __future__ import annotations

import argparse
import numpy as np
from compgeom.algo.hopper_optimizer import HopperOptimizer, hirsch_fitness, neighborly_fitness

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hopper: AI-Assisted Polytope Discovery.")
    parser.add_argument("--dim", type=int, default=3, help="Dimension of the polytope.")
    parser.add_argument("--points", type=int, default=10, help="Number of initial points.")
    parser.add_argument("--iters", type=int, default=100, help="Number of iterations.")
    parser.add_argument("--agents", type=int, default=5, help="Number of agents.")
    parser.add_argument("--scenario", choices=["hirsch", "neighborly"], default="hirsch", help="Discovery scenario.")
    parser.add_argument("--output", type=str, default="best_polytope.npy", help="File to save best polytope points.")

    args = parser.parse_args(argv)

    print(f"Starting Hopper Mission: Scenario={args.scenario}, Dim={args.dim}, Iterations={args.iters}")
    
    optimizer = HopperOptimizer(dim=args.dim, num_initial_points=args.points)
    
    if args.scenario == "hirsch":
        fitness = hirsch_fitness
    else:
        # For k-neighborly, we aim for high facet count per vertex
        fitness = lambda p: neighborly_fitness(p, k=args.dim // 2)

    best_poly, best_fit = optimizer.run(fitness, iterations=args.iters, num_agents=args.agents)

    print("\nMission Complete!")
    print(f"Best Fitness achieved: {best_fit:.4f}")
    print(f"Final Stats: Vertices={best_poly.num_vertices}, Facets={best_poly.num_facets}, Diameter={best_poly.get_diameter()}")
    
    if args.scenario == "hirsch":
        print(f"Hirsch Gap: {best_fit}")
        if best_fit > 0:
            print("!!! COUNTEREXAMPLE FOUND !!!")
        else:
            print("No counterexample found in this run.")

    np.save(args.output, best_poly.points)
    print(f"Saved best polytope to {args.output}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
