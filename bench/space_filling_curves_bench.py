import time
import sys
import os

# Ensure the library is in the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from compgeom.algo.space_filling_curves import SpaceFillingCurves

def run_benchmarks():
    print("Space-Filling Curves Generation Benchmark")
    print("=" * 80)
    
    # 1. Hilbert and Morton (2^L x 2^L)
    print(f"{'Level':<10} | {'N Points':<12} | {'Hilbert (s)':<18} | {'Morton (s)':<18}")
    print("-" * 80)
    for level in range(1, 11): # Up to 1024x1024
        n_points = 4**level
        
        start = time.perf_counter()
        SpaceFillingCurves.hilbert(level)
        t_hilbert = time.perf_counter() - start
        
        start = time.perf_counter()
        SpaceFillingCurves.morton(level)
        t_morton = time.perf_counter() - start
        
        print(f"{level:<10} | {n_points:<12} | {t_hilbert:<18.6f} | {t_morton:<18.6f}")
    
    print("\n")
    
    # 2. Peano (3^L x 3^L)
    print(f"{'Level':<10} | {'N Points':<12} | {'Peano (s)':<18}")
    print("-" * 50)
    for level in range(1, 7): # Up to 729x729 (9^6 = 531,441)
        n_points = 9**level
        
        start = time.perf_counter()
        SpaceFillingCurves.peano(level)
        t_peano = time.perf_counter() - start
        
        print(f"{level:<10} | {n_points:<12} | {t_peano:<18.6f}")

    print("\n")
    
    # 3. Zigzag and Sweep (W x H)
    print(f"{'Width':<10} | {'Height':<10} | {'N Points':<12} | {'Zigzag (s)':<18} | {'Sweep (s)':<18}")
    print("-" * 80)
    for size in [100, 200, 500, 1000]:
        n_points = size * size
        
        start = time.perf_counter()
        SpaceFillingCurves.zigzag(size, size)
        t_zigzag = time.perf_counter() - start
        
        start = time.perf_counter()
        SpaceFillingCurves.sweep(size, size)
        t_sweep = time.perf_counter() - start
        
        print(f"{size:<10} | {size:<10} | {n_points:<12} | {t_zigzag:<18.6f} | {t_sweep:<18.6f}")

if __name__ == "__main__":
    run_benchmarks()
