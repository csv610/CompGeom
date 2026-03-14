import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PoissonDiskSampler import PoissonDiskSampler
import math

def test_poisson_disk_sampler():
    print("Testing PoissonDiskSampler...")
    
    # Test initialization
    sampler = PoissonDiskSampler(dimensions=2, r=0.2, seed=42)
    
    # Test generation
    points = sampler.generate(n_points=10)
    print(f"Generated {len(points)} points.")
    
    # Verify distance constraint
    r = 0.2
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = math.sqrt(sum((points[i][k] - points[j][k])**2 for k in range(2)))
            if dist < r - 1e-9: # small epsilon for float precision
                print(f"FAILED: Points {i} and {j} are too close: {dist} < {r}")
                return False
    
    print("Distance constraint verified.")
    
    # Test N-dimensional generation
    sampler_3d = PoissonDiskSampler(dimensions=3, r=0.3, seed=42)
    points_3d = sampler_3d.generate(n_points=5)
    print(f"Generated {len(points_3d)} 3D points.")
    
    if len(points_3d) > 0:
        print("Test PASSED.")
        return True
    else:
        print("Test FAILED: No points generated.")
        return False

if __name__ == "__main__":
    test_poisson_disk_sampler()
