from geometry_utils import EPSILON, Point, contains_point, cross_product, in_circle


def orientation(a, b, c):
    value = cross_product(a, b, c)
    if value > EPSILON:
        return 1
    if value < -EPSILON:
        return -1
    return 0


def is_point_inside_triangle(point, a, b, c):
    class _TriangleView:
        def __init__(self, vertices):
            self.vertices = vertices

    return contains_point(_TriangleView((a, b, c)), point)


def is_point_inside_circle(point, a, b, c):
    if orientation(a, b, c) == 0:
        return False
    if orientation(a, b, c) < 0:
        b, c = c, b
    return in_circle(a, b, c, point)


if __name__ == "__main__":
    a = Point(0.0, 0.0)
    b = Point(1.0, 0.0)
    c = Point(0.0, 1.0)
    p_triangle = Point(0.2, 0.2)
    p_circle = Point(0.2, 0.2)

    print("orientation(a, b, c) =", orientation(a, b, c))
    print("is_point_inside_triangle =", is_point_inside_triangle(p_triangle, a, b, c))
    print("is_point_inside_circle =", is_point_inside_circle(p_circle, a, b, c))
