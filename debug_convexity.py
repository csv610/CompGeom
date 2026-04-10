from compgeom.kernel import Point2D, orientation_sign

def is_convex(a, b, c, d):
    # Old edge is ab, new edge is cd
    # ABCD is a quadrilateral. To be convex, 
    # c and d must be on opposite sides of ab
    # AND a and b must be on opposite sides of cd
    cond1 = orientation_sign(a, b, c) * orientation_sign(a, b, d) < 0
    cond2 = orientation_sign(c, d, a) * orientation_sign(c, d, b) < 0
    return cond1 and cond2

# Square: (0,0), (1,0), (1,1), (0,1)
# ab = (0,0)-(1,1) [diagonal], c=(1,0), d=(0,1)
a, b = Point2D(0,0), Point2D(1,1)
c, d = Point2D(1,0), Point2D(0,1)
print(f"Square diagonal flip: {is_convex(a, b, c, d)}")

# Non-convex: (0,0), (1,0), (0.1, 0.1), (0,1) [reflex at (0.1, 0.1)]
# ab = (0,0)-(0.1, 0.1), c=(1,0), d=(0,1)
a, b = Point2D(0,0), Point2D(0.1, 0.1)
c, d = Point2D(1,0), Point2D(0,1)
print(f"Non-convex flip: {is_convex(a, b, c, d)}")
