from __future__ import annotations
import math
from dataclasses import dataclass

EPSILON = 1e-9

@dataclass(frozen=True, eq=False, slots=True)
class Point2D:
    x: float
    y: float
    id: int = -1

    def __repr__(self) -> str:
        return f"P{self.id}({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point2D):
            return NotImplemented
        return math.isclose(self.x, other.x, abs_tol=EPSILON) and \
               math.isclose(self.y, other.y, abs_tol=EPSILON)

    def __hash__(self) -> int:
        return hash((round(self.x / EPSILON), round(self.y / EPSILON)))

    def __add__(self, other: Point2D) -> Point2D:
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        return Point2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point2D:
        return Point2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Point2D:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Point2D:
        return Point2D(self.x / scalar, self.y / scalar)

    def dot(self, other: Point2D) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Point2D) -> float:
        """2D cross product (Z-component of 3D cross product)."""
        return self.x * other.y - self.y * other.x

    def length_sq(self) -> float:
        return self.x**2 + self.y**2

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def distance_to(self, other: Point2D) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

@dataclass(frozen=True, eq=False, slots=True)
class Point3D:
    x: float
    y: float
    z: float
    id: int = -1

    def __repr__(self) -> str:
        return f"P{self.id}({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point3D):
            return NotImplemented
        return math.isclose(self.x, other.x, abs_tol=EPSILON) and \
               math.isclose(self.y, other.y, abs_tol=EPSILON) and \
               math.isclose(self.z, other.z, abs_tol=EPSILON)

    def __hash__(self) -> int:
        return hash((round(self.x / EPSILON), round(self.y / EPSILON), round(self.z / EPSILON)))

    def __add__(self, other: Point3D) -> Point3D:
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Point3D) -> Point3D:
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Point3D:
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Point3D:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Point3D:
        return Point3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other: Point3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Point3D) -> Point3D:
        return Point3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length_sq(self) -> float:
        return self.x**2 + self.y**2 + self.z**2

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distance_to(self, other: Point3D) -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
