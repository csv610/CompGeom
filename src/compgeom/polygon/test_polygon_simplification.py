
from compgeom.kernel import Point
from compgeom.polygon import Polygon, make_simple

def test_make_simple():
    print("--- Running Polygon Simplification Tests ---")

    # 1. Figure-8 polygon
    # Points: (0,0), (2,2), (0,2), (2,0)
    # This intersects at (1,1)
    p_fig8 = Polygon([Point(0,0), Point(2,2), Point(0,2), Point(2,0)])
    
    simple_p = p_fig8.make_simple()
    print(f"Original vertices: {len(p_fig8.vertices)}")
    print(f"Simple vertices: {len(simple_p.vertices)}")
    
    # The outer boundary of this figure-8 should be (0,0), (1,1), (2,0), (2,2), (1,1), (0,2) ?
    # Actually, the "outer boundary" heuristic (widest turn) should pick one loop 
    # or the envelope depending on the start.
    # Leftmost-bottommost is (0,0). 
    # From (0,0) to (1,1). At (1,1), options are (2,2) or (0,2) or (2,0).
    
    for i, p in enumerate(simple_p.vertices):
        print(f"  V{i}: {p}")

    # 2. Bowtie
    p_bowtie = Polygon([Point(0,0), Point(2,0), Point(0,2), Point(2,2)])
    simple_bowtie = p_bowtie.make_simple()
    print(f"Bowtie simple vertices: {len(simple_bowtie.vertices)}")
    for i, p in enumerate(simple_bowtie.vertices):
        print(f"  V{i}: {p}")

    print("--- Tests Completed ---")

if __name__ == "__main__":
    test_make_simple()
