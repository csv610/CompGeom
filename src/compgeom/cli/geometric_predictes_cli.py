import argparse

from compgeom import Point2D, contains_point, in_circle, orientation_sign


def is_point_inside_triangle(point, a, b, c):
    return contains_point(a, b, c, point)


def is_point_inside_circle(point, a, b, c):
    orient = orientation_sign(a, b, c)
    if orient == 0:
        return False
    if orient < 0:
        b, c = c, b
    return in_circle(a, b, c, point)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate basic geometric predicates.")
    parser.add_argument("--demo", action="store_true", help="Use the built-in predicate demo.")
    args = parser.parse_args(argv)
    a = Point2D(0.0, 0.0)
    b = Point2D(1.0, 0.0)
    c = Point2D(0.0, 1.0)
    p_triangle = Point2D(0.2, 0.2)
    p_circle = Point2D(0.2, 0.2)

    print("orientation(a, b, c) =", orientation_sign(a, b, c))
    print("is_point_inside_triangle =", is_point_inside_triangle(p_triangle, a, b, c))
    print("is_point_inside_circle =", is_point_inside_circle(p_circle, a, b, c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
