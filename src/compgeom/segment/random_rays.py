import math
import random
import argparse
import sys
import numpy as np

class RandomRayGenerator:
    """
    Generates non-overlapping rays starting from any point and intersecting a circle twice.
    NumPy accelerated clearance checks.
    """
    def __init__(self, radius, min_gap, seed=None):
        self.radius = radius
        self.min_gap = min_gap
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        self.rays = [] # List of [ox, oy, p2x, p2y] where (ox, oy) is origin and p2 is exit point

    def _check_clearance(self, ox, oy, p2x, p2y):
        """Vectorized clearance check against existing ray segments."""
        if not self.rays:
            return True
        
        rays_arr = np.array(self.rays)
        new_p = np.array([[ox, oy], [p2x, p2y]])
        
        # 1. New points to existing segments
        A = rays_arr[:, :2]
        B = rays_arr[:, 2:]
        D = B - A
        L2 = np.sum(D**2, axis=1)
        L2[L2 == 0] = 1e-9
        
        for pt in new_p:
            t = np.clip(np.sum((pt - A) * D, axis=1) / L2, 0, 1)
            proj = A + t[:, np.newaxis] * D
            if np.any(np.sum((pt - proj)**2, axis=1) < self.min_gap**2):
                return False

        # 2. Existing points to new ray segment
        A_n, B_n = new_p[0], new_p[1]
        D_n = B_n - A_n
        L2_n = np.sum(D_n**2)
        if L2_n == 0: L2_n = 1e-9
        
        ex_pts = np.vstack([A, B])
        t_n = np.clip(np.sum((ex_pts - A_n) * D_n, axis=1) / L2_n, 0, 1)
        proj_n = A_n + t_n[:, np.newaxis] * D_n
        if np.any(np.sum((ex_pts - proj_n)**2, axis=1) < self.min_gap**2):
            return False

        # 3. Intersection check
        def ccw_vec(A, B, C):
            return (C[:, 1] - A[:, 1]) * (B[:, 0] - A[:, 0]) > (B[:, 1] - A[:, 1]) * (C[:, 0] - A[:, 0])
        
        C_n, D_n_p = np.full_like(A, ox), np.full_like(A, p2x)
        intersect = (ccw_vec(A, C_n, D_n_p) != ccw_vec(B, C_n, D_n_p)) & \
                    (ccw_vec(A, B, C_n) != ccw_vec(A, B, D_n_p))
        if np.any(intersect):
            return False

        return True

    def generate(self, num_rays, box_scale=2.0):
        self.rays = []
        max_attempts = num_rays * 20000
        limit = self.radius * box_scale
        
        for _ in range(max_attempts):
            if len(self.rays) >= num_rays: break
            
            ox, oy = random.uniform(-limit, limit), random.uniform(-limit, limit)
            angle = random.uniform(0, 2*math.pi)
            dx, dy = math.cos(angle), math.sin(angle)
            
            dot = ox * dx + oy * dy
            origin_sq = ox**2 + oy**2
            disc = dot**2 - (origin_sq - self.radius**2)
            
            if disc <= 0: continue
            
            sqrt_disc = math.sqrt(disc)
            t1 = -dot - sqrt_disc
            t2 = -dot + sqrt_disc
            
            # Forward intersection: both t must be positive (origin outside)
            if t1 > 1e-7 and t2 > 1e-7:
                p2x, p2y = ox + t2 * dx, oy + t2 * dy
                if self._check_clearance(ox, oy, p2x, p2y):
                    self.rays.append([ox, oy, p2x, p2y])
        return self.rays

    def save_to_off(self, filename):
        if not self.rays: return
        with open(filename, 'w') as f:
            f.write(f"OFF\n{len(self.rays)*2} 0 {len(self.rays)}\n")
            for r in self.rays:
                f.write(f"{r[0]:.6f} {r[1]:.6f} 0.000000\n{r[2]:.6f} {r[3]:.6f} 0.000000\n")
            for i in range(len(self.rays)):
                f.write(f"2 {2*i} {2*i+1}\n")

    def visualize(self):
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.add_patch(plt.Circle((0, 0), self.radius, color='r', fill=False))
            for r in self.rays:
                ax.plot([r[0], r[2]], [r[1], r[3]], 'b-', alpha=0.6)
                ax.plot(r[0], r[1], 'ko', markersize=2)
            ax.set_aspect('equal')
            plt.title(f"Generated Rays (n={len(self.rays)})")
            plt.show()
        except ImportError:
            print("Matplotlib not found.")

def main():
    parser = argparse.ArgumentParser(description="Generate non-overlapping rays in a circle (NumPy accelerated).")
    parser.add_argument("-n", "--num", type=int, default=10)
    parser.add_argument("-r", "--radius", type=float, default=10.0)
    parser.add_argument("-g", "--gap", type=float, default=0.5)
    parser.add_argument("-b", "--box", type=float, default=2.0)
    parser.add_argument("-s", "--seed", type=int)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-v", "--visualize", action="store_true")

    args = parser.parse_args()
    try:
        gen = RandomRayGenerator(args.radius, args.gap, args.seed)
        rays = gen.generate(args.num, args.box)
        print(f"Generated {len(rays)} rays.")
        if args.output: gen.save_to_off(args.output)
        if args.visualize: gen.visualize()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
