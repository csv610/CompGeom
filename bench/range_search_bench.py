import time
import random
import sys
import os
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from compgeom.kernel import Point2D, Point3D
from compgeom.mesh.algorithms.range_search import RangeSearch

def naive_sphere_search(points, center, radius):
    c = np.array([center.x, center.y, getattr(center, 'z', 0.0)])
    indices = []
    for i, p in enumerate(points):
        pt = np.array([p.x, p.y, getattr(p, 'z', 0.0)])
        if np.linalg.norm(pt - c) <= radius:
            indices.append(i)
    return indices

def run_benchmarks():
    sizes = [10**2, 10**3, 10**4, 10**5]
    num_queries = 50
    
    print('RangeSearch Scalability Analysis (3D Points)')
    print('=' * 120)
    print(f'{'N Points':<12} | {'Build Time (s)':<15} | {'Sphere Search (ms)':<20} | {'Naive Sphere (ms)':<20}')
    print('-' * 120)
    
    for n in sizes:
        points = [Point3D(random.uniform(0, 1000), random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]
        
        start = time.perf_counter()
        rs = RangeSearch(points)
        build_time = time.perf_counter() - start
        
        sphere_times = []
        for _ in range(num_queries):
            center = Point3D(random.uniform(100, 900), random.uniform(100, 900), random.uniform(100, 900))
            radius = 50.0
            q_start = time.perf_counter()
            rs.within_sphere(center, radius)
            sphere_times.append(time.perf_counter() - q_start)
        avg_sphere = np.mean(sphere_times) * 1000
        
        if n <= 10**4:
            naive_times = []
            for _ in range(10):
                center = Point3D(random.uniform(100, 900), random.uniform(100, 900), random.uniform(100, 900))
                radius = 50.0
                q_start = time.perf_counter()
                naive_sphere_search(points, center, radius)
                naive_times.append(time.perf_counter() - q_start)
            avg_naive = np.mean(naive_times) * 1000
        else:
            avg_naive = float('nan')
            
        print(f'{n:<12} | {build_time:<15.4f} | {avg_sphere:<20.4f} | {avg_naive:<20.4f}')

if __name__ == '__main__':
    run_benchmarks()
