from __future__ import annotations
import math
from dataclasses import dataclass

EPSILON = 1e-9

@dataclass(frozen=True, eq=False, slots=True)
class Point2D:
    """Represents a point in 2D space.

    Attributes:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
        id (int): An optional identifier for the point. Defaults to -1.
    """
    x: float
    y: float
    id: int = -1

    def __repr__(self) -> str:
        """Returns a string representation of the point.

        Returns:
            str: A string in the format 'P{id}({x}, {y})'.
        """
        return f"P{self.id}({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        """Checks if two points are equal within EPSILON.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the other object is a Point2D and its coordinates are within EPSILON.
        """
        if not isinstance(other, Point2D):
            return NotImplemented
        return math.isclose(self.x, other.x, abs_tol=EPSILON) and \
               math.isclose(self.y, other.y, abs_tol=EPSILON)

    def __hash__(self) -> int:
        """Returns the hash of the point.

        Returns:
            int: The hash value based on coordinates rounded by EPSILON.
        """
        return hash((round(self.x / EPSILON), round(self.y / EPSILON)))

    def __add__(self, other: Point2D) -> Point2D:
        """Adds another point to this point.

        Args:
            other (Point2D): The point to add.

        Returns:
            Point2D: A new point representing the sum.
        """
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point2D) -> Point2D:
        """Subtracts another point from this point.

        Args:
            other (Point2D): The point to subtract.

        Returns:
            Point2D: A new point representing the difference.
        """
        return Point2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Point2D:
        """Multiplies the point by a scalar.

        Args:
            scalar (float): The scalar to multiply by.

        Returns:
            Point2D: A new point representing the product.
        """
        return Point2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Point2D:
        """Multiplies the point by a scalar (right multiplication).

        Args:
            scalar (float): The scalar to multiply by.

        Returns:
            Point2D: A new point representing the product.
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Point2D:
        """Divides the point by a scalar.

        Args:
            scalar (float): The scalar to divide by.

        Returns:
            Point2D: A new point representing the quotient.

        Raises:
            ZeroDivisionError: If the scalar is zero.
        """
        return Point2D(self.x / scalar, self.y / scalar)

    def dot(self, other: Point2D) -> float:
        """Calculates the dot product with another point.

        Args:
            other (Point2D): The other point.

        Returns:
            float: The dot product.
        """
        return self.x * other.x + self.y * other.y

    def cross(self, other: Point2D) -> float:
        """Calculates the 2D cross product (Z-component of 3D cross product).

        Args:
            other (Point2D): The other point.

        Returns:
            float: The cross product.
        """
        return self.x * other.y - self.y * other.x

    def length_sq(self) -> float:
        """Calculates the squared length of the point from the origin.

        Returns:
            float: The squared length.
        """
        return self.x**2 + self.y**2

    def length(self) -> float:
        """Calculates the length of the point from the origin.

        Returns:
            float: The length.
        """
        return math.hypot(self.x, self.y)

    def distance_to(self, other: Point2D) -> float:
        """Calculates the Euclidean distance to another point.

        Args:
            other (Point2D): The other point.

        Returns:
            float: The distance.
        """
        return math.hypot(self.x - other.x, self.y - other.y)

@dataclass(frozen=True, eq=False, slots=True)
class Point3D:
    """Represents a point in 3D space.

    Attributes:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
        z (float): The z-coordinate of the point.
        id (int): An optional identifier for the point. Defaults to -1.
    """
    x: float
    y: float
    z: float
    id: int = -1

    def __repr__(self) -> str:
        """Returns a string representation of the point.

        Returns:
            str: A string in the format 'P{id}({x}, {y}, {z})'.
        """
        return f"P{self.id}({self.x}, {self.y}, {self.z})"

    def __eq__(self, other: object) -> bool:
        """Checks if two points are equal within EPSILON.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if the other object is a Point3D and its coordinates are within EPSILON.
        """
        if not isinstance(other, Point3D):
            return NotImplemented
        return math.isclose(self.x, other.x, abs_tol=EPSILON) and \
               math.isclose(self.y, other.y, abs_tol=EPSILON) and \
               math.isclose(self.z, other.z, abs_tol=EPSILON)

    def __hash__(self) -> int:
        """Returns the hash of the point.

        Returns:
            int: The hash value based on coordinates rounded by EPSILON.
        """
        return hash((round(self.x / EPSILON), round(self.y / EPSILON), round(self.z / EPSILON)))

    def __add__(self, other: Point3D) -> Point3D:
        """Adds another point to this point.

        Args:
            other (Point3D): The point to add.

        Returns:
            Point3D: A new point representing the sum.
        """
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Point3D) -> Point3D:
        """Subtracts another point from this point.

        Args:
            other (Point3D): The point to subtract.

        Returns:
            Point3D: A new point representing the difference.
        """
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Point3D:
        """Multiplies the point by a scalar.

        Args:
            scalar (float): The scalar to multiply by.

        Returns:
            Point3D: A new point representing the product.
        """
        return Point3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Point3D:
        """Multiplies the point by a scalar (right multiplication).

        Args:
            scalar (float): The scalar to multiply by.

        Returns:
            Point3D: A new point representing the product.
        """
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Point3D:
        """Divides the point by a scalar.

        Args:
            scalar (float): The scalar to divide by.

        Returns:
            Point3D: A new point representing the quotient.

        Raises:
            ZeroDivisionError: If the scalar is zero.
        """
        return Point3D(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other: Point3D) -> float:
        """Calculates the dot product with another point.

        Args:
            other (Point3D): The other point.

        Returns:
            float: The dot product.
        """
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Point3D) -> Point3D:
        """Calculates the cross product with another point.

        Args:
            other (Point3D): The other point.

        Returns:
            Point3D: The cross product point.
        """
        return Point3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length_sq(self) -> float:
        """Calculates the squared length of the point from the origin.

        Returns:
            float: The squared length.
        """
        return self.x**2 + self.y**2 + self.z**2

    def length(self) -> float:
        """Calculates the length of the point from the origin.

        Returns:
            float: The length.
        """
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def distance_to(self, other: Point3D) -> float:
        """Calculates the Euclidean distance to another point.

        Args:
            other (Point3D): The other point.

        Returns:
            float: The distance.
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
