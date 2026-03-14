import math
import random
import argparse
import sys
import numpy as np

class RandomSegmentGenerator:
    """
    Generates non-overlapping segments in a circle using NumPy for vectorized clearance checks.
    Ensures O(N) check per candidate instead of O(N) loop in pure Python.
    """
    def __init__(self, radius, min_gap, seed=None):
        self.radius = radius
        self.min_gap = min_gap
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        self.segments = [] # List of [x1, y1, x2, y2]

    def _check_clearance(self, x1, y1, x2, y2):
        """Vectorized clearance check against all existing segments."""
        if not self.segments:
            return True
        
        segs = np.array(self.segments)
        new_p = np.array([[x1, y1], [x2, y2]])
        
        # 1. New points to existing segments
        A = segs[:, :2]
        B = segs[:, 2:]
        D = B - A
        L2 = np.sum(D**2, axis=1)
        L2[L2 == 0] = 1e-9
        
        for pt in new_p:
            t = np.clip(np.sum((pt - A) * D, axis=1) / L2, 0, 1)
            proj = A + t[:, np.newaxis] * D
            if np.any(np.sum((pt - proj)**2, axis=1) < self.min_gap**2):
                return False

        # 2. Existing points to new segment
        A_n, B_n = new_p[0], new_p[1]
        D_n = B_n - A_n
        L2_n = np.sum(D_n**2)
        if L2_n == 0: L2_n = 1e-9
        
        ex_pts = np.vstack([A, B])
        t_n = np.clip(np.sum((ex_pts - A_n) * D_n, axis=1) / L2_n, 0, 1)
        proj_n = A_n + t_n[:, np.newaxis] * D_n
        if np.any(np.sum((ex_pts - proj_n)**2, axis=1) < self.min_gap**2):
            return False

        # 3. Robust intersection check
        def ccw_vec(A, B, C):
            return (C[:, 1] - A[:, 1]) * (B[:, 0] - A[:, 0]) > (B[:, 1] - A[:, 1]) * (C[:, 0] - A[:, 0])
        
        C_n, D_n_p = np.full_like(A, x1), np.full_like(A, x2)
        intersect = (ccw_vec(A, C_n, D_n_p) != ccw_vec(B, C_n, D_n_p)) & \
                    (ccw_vec(A, B, C_n) != ccw_vec(A, B, D_n_p))
        if np.any(intersect):
            return False

        return True

    def generate(self, num_segments, min_len, max_len):
        self.segments = []
        max_attempts = num_segments * 5000
        safe_r = self.radius - self.min_gap
        if safe_r <= 0: raise ValueError("Gap too large for radius")

        for _ in range(max_attempts):
            if len(self.segments) >= num_segments: break
            
            r1 = safe_r * math.sqrt(random.random())
            theta1 = random.uniform(0, 2*math.pi)
            x1, y1 = r1 * math.cos(theta1), r1 * math.sin(theta1)
            
            length = random.uniform(min_len, max_len)
            phi = random.uniform(0, 2*math.pi)
            x2, y2 = x1 + length * math.cos(phi), y1 + length * math.sin(phi)
            
            if x2**2 + y2**2 > safe_r**2: continue
            
            if self._check_clearance(x1, y1, x2, y2):
                self.segments.append([x1, y1, x2, y2])
        return self.segments

    def save_to_off(self, filename):
        if not self.segments: return
        with open(filename, 'w') as f:
            f.write(f"OFF\n{len(self.segments)*2} 0 {len(self.segments)}\n")
            for s in self.segments:
                f.write(f"{s[0]:.6f} {s[1]:.6f} 0.000000\n{s[2]:.6f} {s[3]:.6f} 0.000000\n")
            for i in range(len(self.segments)):
                f.write(f"2 {2*i} {2*i+1}\n")

    def visualize(self):
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.add_patch(plt.Circle((0, 0), self.radius, color='r', fill=False))
            for s in self.segments:
                ax.plot([s[0], s[2]], [s[1], s[3]], 'b-')
            ax.set_aspect('equal')
            plt.show()
        except ImportError:
            print("Matplotlib not found.")

def main():
    parser = argparse.ArgumentParser(description="Generate non-overlapping segments in a circle (NumPy accelerated).")
    parser.add_argument("-n", "--num", type=int, default=10)
    parser.add_argument("-min", "--min_len", type=float, default=1.0)
    parser.add_argument("-max", "--max_len", type=float, default=5.0)
    parser.add_argument("-r", "--radius", type=float, default=10.0)
    parser.add_argument("-g", "--gap", type=float, default=0.5)
    parser.add_argument("-s", "--seed", type=int)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-v", "--visualize", action="store_true")

    args = parser.parse_args()
    try:
        gen = RandomSegmentGenerator(args.radius, args.gap, args.seed)
        segs = gen.generate(args.num, args.min_len, args.max_len)
        print(f"Generated {len(segs)} segments.")
        if args.output: gen.save_to_off(args.output)
        if args.visualize: gen.visualize()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
