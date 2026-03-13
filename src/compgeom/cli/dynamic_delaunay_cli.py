import random
from compgeom import Point2D
from compgeom import DynamicDelaunay

def main():
    dt = DynamicDelaunay()
    points = [Point2D(random.randint(0, 100), random.randint(0, 100), i) for i in range(10)]
    print("Adding points incrementally...")
    for p in points: dt.add_point(p)
    tris = dt.get_triangles()
    print(f"Final Triangulation: {len(tris)} triangles.")
    for t in tris: print(f"Triangle: {sorted([v.id for v in t])}")

if __name__ == "__main__":
    main()
