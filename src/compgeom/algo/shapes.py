"""High-level geometric shape objects."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

from compgeom.kernel import Point2D, Point3D
from compgeom.kernel import distance, distance_3d, signed_area_twice


class Shape(ABC):
    """Abstract base class for all geometric shapes."""

    @property
    @abstractmethod
    def centroid(self) -> Union[Point2D, Point3D]:
        """Returns the geometric center of the shape."""
        pass

    @property
    @abstractmethod
    def diameter(self) -> float:
        """Returns the maximum distance between any two points on the shape."""
        pass


class Shape2D(Shape):
    """Abstract base class for 2D shapes."""

    @property
    @abstractmethod
    def area(self) -> float:
        """Returns the area of the shape."""
        pass

    @property
    @abstractmethod
    def perimeter(self) -> float:
        """Returns the perimeter of the shape."""
        pass


class Shape3D(Shape):
    """Abstract base class for 3D shapes."""

    @property
    @abstractmethod
    def volume(self) -> float:
        """Returns the volume of the shape."""
        pass

    @property
    @abstractmethod
    def surface_area(self) -> float:
        """Returns the surface area of the shape."""
        pass


class LineSegment(Shape):
    """A directed line segment between two points (2D or 3D)."""

    def __init__(self, start: Union[Point2D, Point3D], end: Union[Point2D, Point3D]):
        self.start = start
        self.end = end

    @property
    def length(self) -> float:
        if isinstance(self.start, Point3D) and isinstance(self.end, Point3D):
            return distance_3d(self.start, self.end)
        return distance(self.start, self.end)

    @property
    def diameter(self) -> float:
        return self.length

    @property
    def centroid(self) -> Union[Point2D, Point3D]:
        if isinstance(self.start, Point3D) and isinstance(self.end, Point3D):
            return Point3D(
                (self.start.x + self.end.x) / 2.0,
                (self.start.y + self.end.y) / 2.0,
                (self.start.z + self.end.z) / 2.0,
            )
        return Point2D(
            (self.start.x + self.end.x) / 2.0, (self.start.y + self.end.y) / 2.0
        )

    def __repr__(self) -> str:
        return f"LineSegment({self.start} -> {self.end})"


class Ray(Shape):
    """A ray defined by an origin and a direction point (2D or 3D)."""

    def __init__(self, origin: Union[Point2D, Point3D], direction_pt: Union[Point2D, Point3D]):
        self.origin = origin
        self.direction_pt = direction_pt

    @property
    def centroid(self) -> Union[Point2D, Point3D]:
        return self.origin

    @property
    def diameter(self) -> float:
        return float('inf')

    def __repr__(self) -> str:
        return f"Ray(origin={self.origin}, direction_to={self.direction_pt})"


class Circle(Shape2D):
    """A circle defined by a center and a radius."""

    def __init__(self, center: Point2D, radius: float):
        self._center = center
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def centroid(self) -> Point2D:
        return self._center

    @property
    def diameter(self) -> float:
        return 2.0 * self._radius

    @property
    def area(self) -> float:
        return math.pi * (self._radius**2)

    @property
    def perimeter(self) -> float:
        """Returns the circumference of the circle."""
        return 2 * math.pi * self._radius

    def __repr__(self) -> str:
        return f"Circle(center={self._center}, radius={self._radius})"


class Rectangle(Shape2D):
    """An axis-aligned rectangle defined by a center, width, and height."""

    def __init__(self, center: Point2D, width: float, height: float):
        self._center = center
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @property
    def height(self) -> float:
        return self._height

    @property
    def centroid(self) -> Point2D:
        return self._center

    @property
    def diameter(self) -> float:
        return math.sqrt(self._width**2 + self._height**2)

    @property
    def area(self) -> float:
        return self._width * self._height

    @property
    def perimeter(self) -> float:
        return 2 * (self._width + self._height)

    @property
    def vertices(self) -> List[Point2D]:
        """Returns the four corners of the rectangle."""
        hw, hh = self._width / 2.0, self._height / 2.0
        return [
            Point2D(self._center.x - hw, self._center.y - hh),
            Point2D(self._center.x + hw, self._center.y - hh),
            Point2D(self._center.x + hw, self._center.y + hh),
            Point2D(self._center.x - hw, self._center.y + hh),
        ]

    def __repr__(self) -> str:
        return f"Rectangle(center={self._center}, width={self._width}, height={self._height})"


class Square(Rectangle):
    """A square defined by a center and a side length."""

    def __init__(self, center: Point2D, side_length: float):
        super().__init__(center, side_length, side_length)

    @property
    def side_length(self) -> float:
        return self.width

    def __repr__(self) -> str:
        return f"Square(center={self.centroid}, side={self.side_length})"


class Triangle(Shape2D):
    """A triangle defined by three vertices."""

    def __init__(self, a: Point2D, b: Point2D, c: Point2D):
        self.a = a
        self.b = b
        self.c = c

    @property
    def centroid(self) -> Point2D:
        return Point2D((self.a.x + self.b.x + self.c.x) / 3.0, (self.a.y + self.b.y + self.c.y) / 3.0)

    @property
    def diameter(self) -> float:
        from compgeom.polygon.polygon import get_convex_diameter
        return get_convex_diameter([self.a, self.b, self.c])

    @property
    def area(self) -> float:
        return abs(signed_area_twice([self.a, self.b, self.c])) / 2.0

    @property
    def perimeter(self) -> float:
        return distance(self.a, self.b) + distance(self.b, self.c) + distance(self.c, self.a)

    def __repr__(self) -> str:
        return f"Triangle({self.a}, {self.b}, {self.c})"


class Plane(Shape):
    """A 3D plane defined by a point and a normal vector."""

    def __init__(self, point: Point3D, normal: Tuple[float, float, float]):
        self.point = point
        self.normal = normal

    @property
    def centroid(self) -> Point3D:
        return self.point

    @property
    def diameter(self) -> float:
        return float('inf')

    def __repr__(self) -> str:
        return f"Plane(point={self.point}, normal={self.normal})"


class Tetrahedron(Shape3D):
    """A tetrahedron defined by four 3D vertices."""

    def __init__(self, a: Point3D, b: Point3D, c: Point3D, d: Point3D):
        self.vertices = (a, b, c, d)

    @property
    def centroid(self) -> Point3D:
        return Point3D(
            sum(v.x for v in self.vertices) / 4.0,
            sum(v.y for v in self.vertices) / 4.0,
            sum(v.z for v in self.vertices) / 4.0,
        )

    @property
    def diameter(self) -> float:
        # Max distance between any two vertices
        max_d = 0.0
        v = self.vertices
        for i in range(4):
            for j in range(i + 1, 4):
                max_d = max(max_d, distance_3d(v[i], v[j]))
        return max_d

    @property
    def volume(self) -> float:
        a, b, c, d = self.vertices
        # Volume = |(a-d) . ((b-d) x (c-d))| / 6
        v1 = (a.x - d.x, a.y - d.y, a.z - d.z)
        v2 = (b.x - d.x, b.y - d.y, b.z - d.z)
        v3 = (c.x - d.x, c.y - d.y, c.z - d.z)
        cp = (
            v2[1] * v3[2] - v2[2] * v3[1],
            v2[2] * v3[0] - v2[0] * v3[2],
            v2[0] * v3[1] - v2[1] * v3[0],
        )
        dot = v1[0] * cp[0] + v1[1] * cp[1] + v1[2] * cp[2]
        return abs(dot) / 6.0

    @property
    def surface_area(self) -> float:
        a, b, c, d = self.vertices

        def tri_area(p1, p2, p3):
            # Using 3D cross product area formula
            v1 = (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
            v2 = (p3.x - p1.x, p3.y - p1.y, p3.z - p1.z)
            cp = (
                v1[1] * v2[2] - v1[2] * v2[1],
                v1[2] * v2[0] - v1[0] * v2[2],
                v1[0] * v2[1] - v1[1] * v2[0],
            )
            return 0.5 * math.sqrt(cp[0] ** 2 + cp[1] ** 2 + cp[2] ** 2)

        return (
            tri_area(a, b, c) + tri_area(a, b, d) + tri_area(a, c, d) + tri_area(b, c, d)
        )

    def __repr__(self) -> str:
        return f"Tetrahedron({self.vertices})"


class Sphere(Shape3D):
    """A sphere defined by a center and a radius."""

    def __init__(self, center: Point3D, radius: float):
        self._center = center
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def centroid(self) -> Point3D:
        return self._center

    @property
    def diameter(self) -> float:
        return 2.0 * self._radius

    @property
    def volume(self) -> float:
        return (4.0 / 3.0) * math.pi * (self._radius**3)

    @property
    def surface_area(self) -> float:
        return 4.0 * math.pi * (self._radius**2)

    def __repr__(self) -> str:
        return f"Sphere(center={self._center}, radius={self._radius})"


class Cuboid(Shape3D):
    """A 3D cuboid (box) defined by a center and dimensions."""

    def __init__(self, center: Point3D, width: float, height: float, depth: float):
        self._center = center
        self._width = width
        self._height = height
        self._depth = depth

    @property
    def centroid(self) -> Point3D:
        return self._center

    @property
    def diameter(self) -> float:
        return math.sqrt(self._width**2 + self._height**2 + self._depth**2)

    @property
    def volume(self) -> float:
        return self._width * self._height * self._depth

    @property
    def surface_area(self) -> float:
        return 2 * (
            self._width * self._height
            + self._height * self._depth
            + self._width * self._depth
        )

    def __repr__(self) -> str:
        return f"Cuboid(center={self._center}, w={self._width}, h={self._height}, d={self._depth})"


class Hexahedron(Shape3D):
    """A general hexahedron defined by eight 3D vertices."""

    def __init__(self, vertices: List[Point3D]):
        if len(vertices) != 8:
            raise ValueError("A hexahedron must have exactly 8 vertices.")
        self.vertices = tuple(vertices)

    @property
    def centroid(self) -> Point3D:
        return Point3D(
            sum(v.x for v in self.vertices) / 8.0,
            sum(v.y for v in self.vertices) / 8.0,
            sum(v.z for v in self.vertices) / 8.0,
        )

    @property
    def diameter(self) -> float:
        max_d = 0.0
        v = self.vertices
        for i in range(8):
            for j in range(i + 1, 8):
                max_d = max(max_d, distance_3d(v[i], v[j]))
        return max_d

    @property
    def volume(self) -> float:
        """Calculates volume by decomposing into 5 tetrahedra."""
        v = self.vertices
        # Assuming standard ordering: 0-3 bottom face, 4-7 top face
        # One possible decomposition:
        t1 = Tetrahedron(v[0], v[1], v[2], v[5])
        t2 = Tetrahedron(v[0], v[2], v[3], v[7])
        t3 = Tetrahedron(v[0], v[5], v[7], v[4])
        t4 = Tetrahedron(v[2], v[5], v[7], v[6])
        t5 = Tetrahedron(v[0], v[2], v[5], v[7])
        return t1.volume + t2.volume + t3.volume + t4.volume + t5.volume

    @property
    def surface_area(self) -> float:
        """Calculates surface area as the sum of 6 quadrilateral faces (triangulated)."""
        v = self.vertices

        def quad_area(p1, p2, p3, p4):
            # Sum of two triangles
            def tri_area(a, b, c):
                v1 = (b.x - a.x, b.y - a.y, b.z - a.z)
                v2 = (c.x - a.x, c.y - a.y, c.z - a.z)
                cp = (
                    v1[1] * v2[2] - v1[2] * v2[1],
                    v1[2] * v2[0] - v1[0] * v2[2],
                    v1[0] * v2[1] - v1[1] * v2[0],
                )
                return 0.5 * math.sqrt(cp[0] ** 2 + cp[1] ** 2 + cp[2] ** 2)

            return tri_area(p1, p2, p3) + tri_area(p1, p3, p4)

        # Standard face indices for a box-like hexahedron
        faces = [
            (0, 3, 2, 1), # Bottom
            (4, 5, 6, 7), # Top
            (0, 1, 5, 4), # Front
            (2, 3, 7, 6), # Back
            (0, 4, 7, 3), # Left
            (1, 2, 6, 5), # Right
        ]
        return sum(quad_area(v[f[0]], v[f[1]], v[f[2]], v[f[3]]) for f in faces)

    def __repr__(self) -> str:
        return f"Hexahedron({len(self.vertices)} vertices)"


class Cube(Hexahedron):
    """A cube defined by a center and a side length."""

    def __init__(self, center: Point3D, side_length: float):
        self._center = center
        self._side = side_length
        # Generate vertices for Hexahedron decomposition
        hs = side_length / 2.0
        v = [
            Point3D(center.x - hs, center.y - hs, center.z - hs),
            Point3D(center.x + hs, center.y - hs, center.z - hs),
            Point3D(center.x + hs, center.y + hs, center.z - hs),
            Point3D(center.x - hs, center.y + hs, center.z - hs),
            Point3D(center.x - hs, center.y - hs, center.z + hs),
            Point3D(center.x + hs, center.y - hs, center.z + hs),
            Point3D(center.x + hs, center.y + hs, center.z + hs),
            Point3D(center.x - hs, center.y + hs, center.z + hs),
        ]
        super().__init__(v)

    @property
    def side_length(self) -> float:
        return self._side

    @property
    def centroid(self) -> Point3D:
        return self._center

    @property
    def diameter(self) -> float:
        return math.sqrt(3.0) * self._side

    @property
    def volume(self) -> float:
        return self._side**3

    @property
    def surface_area(self) -> float:
        return 6.0 * (self._side**2)

    def __repr__(self) -> str:
        return f"Cube(center={self.centroid}, side={self.side_length})"


__all__ = [
    "Circle",
    "Cube",
    "Cuboid",
    "Hexahedron",
    "LineSegment",
    "Plane",
    "Ray",
    "Rectangle",
    "Shape",
    "Shape2D",
    "Shape3D",
    "Sphere",
    "Square",
    "Tetrahedron",
    "Triangle",
]
