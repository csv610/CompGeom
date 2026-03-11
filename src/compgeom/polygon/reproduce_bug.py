
from compgeom.kernel import Point
from compgeom.polygon.polygon_guards import solve_art_gallery

def test_triangle():
    print("Testing triangle...")
    poly = [Point(0, 0), Point(1, 0), Point(0, 1)]
    guards = solve_art_gallery(poly)
    print(f"Guards: {guards}")
    assert len(guards) == 1

def test_square():
    print("Testing square...")
    poly = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)]
    guards = solve_art_gallery(poly)
    print(f"Guards: {guards}")
    assert len(guards) == 1

def test_l_shape():
    print("Testing L-shape...")
    poly = [
        Point(0, 0), Point(2, 0), Point(2, 1), Point(1, 1), Point(1, 2), Point(0, 2)
    ]
    guards = solve_art_gallery(poly)
    print(f"Guards: {guards}")
    # n=6, floor(6/3) = 2 guards max.
    assert len(guards) <= 2

if __name__ == "__main__":
    try:
        test_triangle()
        test_square()
        test_l_shape()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
