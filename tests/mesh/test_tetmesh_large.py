import time
import random
from compgeom.kernel import Point3D
from compgeom.mesh.volume.tetmesh import tetmesher

def test_large_random_points():
    num_points = 10
    random.seed(42)
    points = [
        Point3D(random.uniform(0, 100), random.uniform(0, 100), random.uniform(0, 100), id=i)
        for i in range(num_points)
    ]
    
    start_time = time.time()
    mesh = tetmesher(points)
    end_time = time.time()
    
    duration = end_time - start_time
    print(f'Triangulated {num_points} points in {duration:.4f} seconds.')
    print(f'Generated {len(mesh.cells)} tetrahedra.')
    
    assert len(mesh.cells) > 0
    assert len(mesh.vertices) == num_points
    
    for cell in mesh.cells:
        assert len(set(cell)) == 4

if __name__ == '__main__':
    test_large_random_points()
